#!/usr/bin/env python -u
# -*- coding: utf-8 -*-


'''
start the test with a role
'''

import os
import time

from device_tools import getDeviceList

from tester import Tester

def _walk():
    '''
    walk the current folder, when has unique apk and android test apk file, get it
    '''
    targetApk = None
    testApk = None

    curPath = os.path.realpath(".")
    for fname in os.listdir(curPath):
        if fname.endswith(".apk"):
            if targetApk is not None and testApk is not None:
                raise Exception("have many apk files in this folder: <" + curPath + ">")

            if fname.endswith("-androidTest.apk"):
                testApk = fname
            else:
                targetApk = fname

    if targetApk is None or testApk is None:
        raise Exception("can't found the target apk file(end with .apk) and test apk file(end with -andoridTest.apk) in this folder: <" + curPath + ">")

    return [targetApk, testApk]


if __name__ == "__main__":
    enters = {
              # publish stream
              "anchor": "com.zego.livedemo5.startWithAnchor", 
              # join live or watch only
              "audience": "com.zego.livedemo5.startWithPlay",
              # test setting combinations
              "setting": "com.zego.livedemo5.testSettings",
              # run all test case
              "test": None
              }

    import argparse
    parse = argparse.ArgumentParser()

    parse.add_argument('-a', '--target', action = 'store', type = str, help = "the apk file that will be test")
    parse.add_argument('-t', '--test', action = 'store', type = str, help = "android test apk file path")

    parse.add_argument('-r', '--role', action = 'store', type = str, choices = enters.keys(), help = "special the start role")
    args = parse.parse_args()

    enterPkg = enters[args.role]
    if args.target and args.test:
        targetApk, testApk = args.target, args.test
    else:
        targetApk, testApk = _walk()

    beginTime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    scriptRoot = os.path.split(os.path.realpath(__file__))[0]
    resultPath = scriptRoot
    try:
        resultPath = os.path.join(scriptRoot, beginTime)
        os.mkdir(resultPath)
    except Exception, e:
        resultPath = scriptRoot
        print (e)

    devices = getDeviceList()
    print ("===" * 5 + " device list " + "===" * 5)
    print (os.linesep.join(['->'.join(device) for device in devices]))
    print ("===" * 14)
    threads = []
    local_port = 5555
    for device in devices:
        tester = Tester(targetApk, testApk, enterPkg)
        tester.setDevice(device[0], local_port).setOutputPath(resultPath)
        t = tester.doRun()
        threads.append(t)
        local_port += 1

    for t in threads:
        print ("call %s's join" % t.getName())
        t.join()

    print ("finish.")
