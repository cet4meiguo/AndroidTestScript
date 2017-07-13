#!/usr/bin/env python -u
# -*- coding: utf-8 -*-


'''download the uiautomator from : https://github.com/xiaocong/uiautomator, then enter the uiautomator folder and run ./setup.py install
will install uiautomator apk and it's test apk when first run uiautomator

announce: 测试应用与主应用需要采用相同签名，默认编译的是 debug 版本，如需编译 release 或者其它版本，只需在 build.gradle 的 android 节点指定 testBuildType
'''

import os, sys
import threading, thread, signal
import time

from cmd_tools import fixCmd, asyncExec, getstatusoutput
from adb_tools import getPackageName, uninstallPackages, installApkInSilent, clearData
from device_tools import getDeviceList

class _ResourceCapturer(threading.Thread):
    '''
    dump zego's process cpu info and memory info
    '''
    def __init__(self, deviceId, pkgName, resultPath,isAnchor=""):
        super(_ResourceCapturer, self).__init__(name="captureResource-%s" % deviceId)
        self._stopFlag = False
        self._stop = False
        self._deviceId = deviceId
        self._targetPkgName = pkgName
        self._resultPath = resultPath
        self._isAnchor=isAnchor
        now = time.strftime("%H:%M:%S", time.localtime())
        data=now.split(":")
        self._startTime=int(data[0])*3600+int(data[1])*60+int(data[2])

    def _getPId(self, cmdName, isPhone = True):
        if isPhone:
            cmd = '''adb -s %s shell ps | grep "%s"''' % (self._deviceId, cmdName)
            splitNum = 8
            idIndex = 1
        else:
            sepPos = cmdName.find('|')
            if sepPos > 0:
                cmdName = cmdName[ : sepPos].rstrip()
            cmd = '''ps | grep "%s"''' % cmdName
            splitNum = 3
            idIndex = 0

        sts, text = getstatusoutput(cmd)
        if sts == 0:
            lines = text.split('\n')
            for line in lines:
                items = line.split(None, splitNum)
                if items[-1].strip() == cmdName:
                    return items[idIndex]
        raise Exception("special command<%s> not running in now" % cmdName)

    def _dumpMemInfo(self, cmd):
        '''
        dumpsys meminfo [pid] | grep TOTAL, return:

        '''
        sts, text = getstatusoutput(cmd, False)
        if sts == 0:
            return text.split()[1:]
        return []

    def _parseCpuInfo(self, line):
        data = line.split()

        return [data[2].strip('%'), data[5].strip('K'), data[6].strip('K')]

    def _saveItem(self, fp, info):
        if info:
            fp.write('\t'.join(info))
            fp.write('\r\n')

    def _safeClose(self, fp):
        if fp:
            fp.write('\r\n')
            fp.flush()
            fp.close()

    def run(self):
        # wait for target process is running
        targetPId = -1;
        while targetPId < 0:
            if self._stopFlag:
                self._stop = True
                thread.exit()
                return

            time.sleep(0.2)
            try:
                targetPId = self._getPId(self._targetPkgName)
            except Exception, e:
                print (e)
                continue

        outPath = os.path.join(self._resultPath, (self._deviceId+self._isAnchor))
        if not os.path.exists(outPath):
            os.mkdir(outPath)
        
        fp_mem = open(os.path.join(outPath, "mem_info.txt"), 'w')
        fp_mem.write("DateTime\tPssTotal\tPrivateDirty\tPrivateClean\tSwappedDirty\tHeapSize\tHeapAlloc\tHeapFree\r\n")

        fp_cpu = open(os.path.join(outPath, "cpu_info.txt"), 'w')
        fp_cpu.write("DateTime\tCPU%\tVSS(K)\tRSS(K)\r\n")

        self._cmd_dump_meminfo = "adb -s %s shell dumpsys meminfo %s | grep TOTAL" % (self._deviceId, targetPId)
        self._cmd_dump_cpuinfo = "adb -s %s shell top -d 1.5" % (self._deviceId)
        
        FLUSH_FREQUENCY = 6
        cnt = 1

        for line in asyncExec(self._cmd_dump_cpuinfo, self.needStop):
            if line.find(targetPId) >= 0:
                now = time.strftime("%H:%M:%S", time.localtime())
                data=now.split(":")
                curTime=int(data[0])*3600+int(data[1])*60+int(data[2])
                curTime=curTime-self._startTime
                cpuInfo = self._parseCpuInfo(line)
                if cpuInfo:
                    cpuInfo.insert(0, str(curTime))
                    self._saveItem(fp_cpu, cpuInfo)

                memInfo = self._dumpMemInfo(self._cmd_dump_meminfo)
                if memInfo:
                    memInfo.insert(0, str(curTime))
                    self._saveItem(fp_mem, memInfo)

                cnt += 1
                if cnt % FLUSH_FREQUENCY == 0: 
                    fp_mem.flush()
                    fp_cpu.flush()

            if self._stopFlag:
                break

        self._safeClose(fp_mem)
        self._safeClose(fp_cpu)

        self._stop = True
        thread.exit()

    def needStop(self):
        return self._stopFlag

    def syncStop(self):
        self._stopFlag = True
        try:
            if self._cmd_dump_cpuinfo is not None:
                top_pid = self._getPId(self._cmd_dump_cpuinfo, isPhone = False)
                print ("send terminal signal to process: " + top_pid)
                os.kill(int(top_pid), signal.SIGTERM)
        except Exception, e:
            print (e)

        try:
            if self._cmd_dump_meminfo is not None:
                mem_pid = self._getPId(self._cmd_dump_meminfo, isPhone = False)
                print ("send terminal signal to process: " + mem_pid)
                os.kill(int(mem_pid), signal.SIGTERM)
        except Exception, e:
            print (e)

        while not self._stop:
            time.sleep(0.1)

        print ("end capture.")

class Tester(object):
    def __init__(self, targetApk, testApk, enterPkg, enterCls = None):
        self._targetApk = targetApk
        self._testApk = testApk
        self._enterPkg = enterPkg
        self._enterCls = enterCls
        self._targetPkg = getPackageName(targetApk)

        # run on first device when not special device info
        self._local_port = 5555
        self._deviceId = None

    def _uninstallOldVersion(self):
        packages = (self._targetPkg, "{0}.test".format(self._targetPkg))
        uninstallPackages(packages, deviceId = self._deviceId)
        

    def _installLatestVersion(self):
        apks = (self._targetApk, self._testApk)
        installApkInSilent(apks, deviceId = self._deviceId, localPort = self._local_port)

    def _clearEnv(self):
        '''
        must clear com.github.uiautomator and com.github.uiautomator.test's data befor run test instance, because has used the uiautomatorin in test instance also
        '''
        clearData("com.github.uiautomator", "com.github.uiautomator.test", deviceId = self._deviceId)

    def _startJunitTest(self):
        cmd = '''adb -s %s shell am instrument -w -r -e debug false''' % self._deviceId
        if self._enterCls:
            cmd = '''%s -e class %s ''' % (cmd, self._enterCls)
        elif self._enterPkg:
            cmd = '''%s -e package %s ''' % (cmd, self._enterPkg)
        else:
            pass
        cmd = '''%s %s.test/android.support.test.runner.AndroidJUnitRunner''' % (cmd, self._targetPkg)
        sts, text = getstatusoutput(cmd)

        outPath = os.path.join(self._resultPath, (self._deviceId+self._isAnchor))
        if not os.path.exists(outPath):
            os.mkdir(outPath)
        resultFile = os.path.join(outPath, "result.txt")
        fp = open(resultFile, "w")
        data = "\r\n".join((str(sts), text))
        fp.write(data)
        fp.close()
        print (data)

    def _pullLiveQualityLog(self):
        outPath = os.path.join(self._resultPath, (self._deviceId+self._isAnchor))
        if not os.path.exists(outPath):
            os.mkdir(outPath)

        targetPath = os.path.join(outPath, "livequality.log")
        print "self=",self._deviceId, self._targetPkg, targetPath
        #cmd = "adb -s %s pull /sdcard/zego_livedemo_live_quality.log %s" % (self._deviceId, targetPath)
        cmd = "adb -s %s pull /sdcard/Android/%s/cache/zego_livedemo_live_quality.log %s" % (self._deviceId, self._targetPkg, targetPath)
        sts, text = getstatusoutput(cmd)
        print ("*** %d : %s ***\r\n" % (sts, text))

    def _attachDefaultDevice(self):
        devices = getDeviceList()
        if not devices:
            raise Exception("no device be found")
        else:
            self._deviceId = devices[0][0]

    def setDevice(self, deviceId, localPort):
        self._deviceId = deviceId
        self._local_port = localPort
        return self

    def setOutputPath(self, resultPath,isAnchor=""):
        self._resultPath = resultPath
        self._isAnchor=isAnchor
        return self

    def doRun(self):
        parent = self
        class Runner(threading.Thread):
            def __init__(self, name=None):
                super(Runner, self).__init__(name=name)

            def run(self):
                print ("doRun for: %s" % parent._deviceId)
                parent._uninstallOldVersion()
                #parent._clearEnv(deviceId)  #避免上次执行过程中异常中断未清理uiautomator的相关数据
                parent._installLatestVersion();
                parent._clearEnv()  #必须清理uiautomator数据才能让被测试App中正常调用 uiautomator 相关功能
                capturer = _ResourceCapturer(parent._deviceId, parent._targetPkg, parent._resultPath,parent._isAnchor)
                capturer.setDaemon(True)
                capturer.start()
                parent._startJunitTest()
                capturer.syncStop()
                parent._pullLiveQualityLog()
                print ("end doRun for %s" % parent._deviceId)

        if not self._deviceId:
            self._attachDefaultDevice()

        r = Runner("mainRun-%s" % self._deviceId)
        r.setDaemon(True)
        r.start()
        return r


if __name__ == "__main__":
    DEFAULT_TARGET_APK = "app-release.apk"
    DEFAULT_INSTRUMENT_TEST_APK = "app-release-androidTest.apk"
    DEFAULT_ENTER_PACKAGE = "com.zego.livedemo5.startWithAnchor"

    import argparse
    parse = argparse.ArgumentParser()

    parse.add_argument('-target', action = 'store', type = str, help = "the apk file that will be test")
    parse.add_argument('-test', action = 'store', type = str, help = "android test apk file path")
    parse.add_argument('-epackage', action = 'store', type = str, help = "test enter package name")
    parse.add_argument('-eclass', action = 'store', type = str, help = "test enter class name, can contain the special method with '#'")
    args = parse.parse_args()

    targetApk = DEFAULT_TARGET_APK
    testApk = DEFAULT_INSTRUMENT_TEST_APK
    enterPkg = DEFAULT_ENTER_PACKAGE
    enterCls = None
    if args.target:
        targetApk = args.target
    if args.test:
        testApk = args.test
    if args.epackage:
        enterPkg = args.epackage
    if args.eclass:
        enterCls = args.eclass

    beginTime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    scriptRoot = os.path.split(os.path.realpath(__file__))[0]
    resultPath = scriptRoot
    try:
        resultPath = os.path.join(scriptRoot, beginTime)
        os.mkdir(resultPath)
    except Exception, e:
        resultPath = scriptRoot
        print (e)

    tester = Tester(targetApk, testApk, enterPkg, enterCls)
    devices = getDeviceList()
    if not devices:
        raise Exception("no device be found")
    elif len(devices) == 1:
        print ("run on device: " + '->'.join(devices[0]))
        tester.setDevice(devices[0][0], 5555)
    else:
        i = 0
        for device in devices:
            i += 1
            print ("{}. {}".format(i, ' '.join(device)))

        index = -1
        indexStr = raw_input("select a device to run test [1-{}]: ".format(i))
        while True:
            try:
                index = int(indexStr)
            except Exception, e:
                pass

            if index < 1 or index > i:
                indexStr = raw_input("input must be integer and in [1-{}], reselect:".format(i))
            else:
                tester.setDevice(devices[index - 1][0], 5555)
                break

    tester.setOutputPath(resultPath)
    tester.doRun().join()

    print ("finish.")

