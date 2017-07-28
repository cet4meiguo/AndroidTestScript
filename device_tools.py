#!/usr/bin/env python -u
#coding: utf-8

from cmd_tools import getstatusoutput
import re

def _getprop(deviceId, propName):
    cmd = '''adb -s {} shell getprop {}'''.format(deviceId, propName)
    sts, text = getstatusoutput(cmd)
    return text if sts == 0 else ""

def _getManufacturer(deviceId):
    return _getprop(deviceId, "ro.product.manufacturer")

def _manufacturerContain(deviceId, text):
    manufacturer = _getManufacturer(deviceId)
    return True if manufacturer.lower().find(text.lower()) >= 0 else False

def _getFingerPrint(deviceId):
    return _getprop(deviceId, "ro.build.fingerprint")
    
def _fingerPrintContain(deviceId, text):
    fingerprint = _getFingerPrint(deviceId)
    return True if fingerprint.lower().find(text.lower()) >= 0 else False

def isMeizuOs(deviceId):
    return _fingerPrintContain(deviceId, "meizu") or _manufacturerContain(deviceId, "meizu")

def isMIUI(deviceId):
    return _fingerPrintContain(deviceId, "xiaomi") or _manufacturerContain(deviceId, "xiaomi")

def getDeviceList():
    sts, text = getstatusoutput("adb devices -l")
    if sts == 0:
        lines = [line.strip() for line in text.split('\n')[1:] if (len(line.strip()) > 0 and not line.startswith('*'))]
        devices = []
        for item in lines:
            parts = item.split()
            devices.append((parts[0], ' '.join(parts[1:])))
        return devices
    return []

# 获取每一部设备对应的名字和型号
def getDeviceNameAndModel():
    devicesList=getDeviceList()
    ans={}
    for d in devicesList:
        sts,text=getstatusoutput("adb -s %s shell cat /system/build.prop | grep 'product'" % (d[0]))
        result=[]
        if sts==0:
            manufacturer=re.match(r'.*manufacturer=([^\r\n]*).*',text,re.I|re.M|re.S)
            if manufacturer:
                result.append(manufacturer.group(1))
            model=re.match(r'.*model=([^\r\n]*).*',text,re.I|re.M|re.S)
            if model:
                result.append(model.group(1))
        ans[d[0]]='-'.join(result)
    # print(ans)
    return ans
def getVersionName(package):
    devices=getDeviceList()
    if len(devices)>=1:
        sts,text=getstatusoutput("adb -s %s shell dumpsys package %s | grep versionName"%(devices[0][0],package))
        if sts==0:
            print("versionName="+text[text.index("=")+1:])
            return text[text.index("=")+1:text.index("=")+10]
    return "versionNameError"

# 设置屏幕常亮
def setScreenAlwaysOn():
    devices=getDeviceList()
    for device in devices:
        getstatusoutput("adb -s %s shell svc power stayon true"%device[0])

# 取消屏幕常亮
def cancelScreenAlwaysOn():
    devices=getDeviceList()
    for device in devices:
        getstatusoutput("adb -s %s shell svc power stayon false"%device[0])

def lockDevicesScreen():
    devices=getDeviceList()
    for device in devices:
        getstatusoutput("adb -s %s shell input keyevent 223"%device[0])
        

if __name__ == "__main__":
    print ("judge the os type with manufacturer")
    getDeviceModel()
