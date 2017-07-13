#!/usr/bin/env python -u
#coding:utf-8


import re

import threading, time

from uiautomator import Device

from cmd_tools import getstatusoutput
from device_tools import *

def getPackageName(apkFile):
    cmd = "./aapt dump badging %s | grep package:" % apkFile
    sts, text = getstatusoutput(cmd)
    if sts == 0:
        m = re.match(r"package: name='([\S]+)'", text)
        if m:
            return m.groups()[0]
    raise Exception("can't match the package name in apk <%s>" % apkFile) 

def uninstallPackages(*packageList, **deviceInfo):
    deviceId = deviceInfo['deviceId'] if deviceInfo.has_key('deviceId') else None
    packages = _extendTupleArgs(packageList)
    for p in packages:
        if deviceId is None:
            cmd = "adb uninstall %s" % p
        else:
            cmd = "adb -s %s uninstall %s" % (deviceId, p)
        sts, text = getstatusoutput(cmd)
        print ("*** return status: %d-%s for %s ***\r\n" % (sts, text, deviceId))

def installApkInSilent(*apkFiles, **deviceInfo):
    '''
    install a lot of apk files to phone
    '''
    deviceId = deviceInfo['deviceId'] if deviceInfo.has_key('deviceId') else None
    localPort = int(deviceInfo['localPort']) if deviceInfo.has_key("localPort") else 5555

    installWatcher = _InstallDialogAndAgreeWatcher(deviceId, localPort, "watcher-%s-%d" % (deviceId, localPort))
    installWatcher.setDaemon(True)
    installWatcher.start()

    apks = _extendTupleArgs(apkFiles)
    for apkFile in apks:
        if deviceId is None:
            cmd = "adb install %s" % apkFile
        else:
            cmd = "adb -s %s install %s" % (deviceId, apkFile)
        sts, text = getstatusoutput(cmd)
        print ("*** return status: %d for %s ***\r\n" % (sts, deviceId))

    installWatcher.syncStop()

def clearData(*packages, **deviceInfo):
    pkgNames = _extendTupleArgs(packages)
    deviceId = deviceInfo['deviceId'] if deviceInfo.has_key('deviceId') else None
    for packageName in pkgNames:
        if deviceId is None:
            cmd = "adb shell pm clear %s" % packageName
        else:
            cmd = "adb -s %s shell pm clear %s" % (deviceId, packageName)
        sts, text = getstatusoutput(cmd)
        print ("*** %d : %s ***\r\n" % (sts, text))

def _extendTupleArgs(*listArgs):
    def __extend(value, result):
        for e in value:
            if type(e) == tuple or type(e) == list:
                __extend(e, result)
            else:
                result.append(e)

    elems = []
    for elem in listArgs:
        if type(elem) == tuple or type(elem) == list:
            __extend(elem, elems)
        else:
            elems.append(elem)
    return elems

class _InstallDialogAndAgreeWatcher(threading.Thread):
    '''click the allow use uiautomator's watcher'''
    def __init__(self, deviceId, localPort, name):
        super(_InstallDialogAndAgreeWatcher, self).__init__(name=name)
        self._stopFlag = False
        self._stop = False
        self.d = Device() if deviceId is None else Device(deviceId, localPort)
        if isMeizuOs(deviceId):
            self.d.watcher('installApk').when(text=u"允许").when(textContains=u"正在通过USB自动安装").click(text=u"允许", className="android.widget.Button")
        elif isMIUI(deviceId):
            self.d.watcher('installApk').when(text=u"继续安装").when(textContains=u"USB安装提示").click(text=u"继续安装", className="android.widget.TextView")
        else:
            print("adb_tools-->not Meizu os MIUI,pass")
            pass
    
    def run(self):
        while not self._stopFlag:
            result = self.d.watchers.run()
            time.sleep(0.5)

        self.d.watchers.remove()
        self._stop = True

    def syncStop(self):
        self._stopFlag = True
        while not self._stop:
            time.sleep(0.1)

if __name__ == "__main__":
    print ("manager the package(s) for mobile device")
