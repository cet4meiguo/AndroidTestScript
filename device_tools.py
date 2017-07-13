#!/usr/bin/env python -u
#coding: utf-8

from cmd_tools import getstatusoutput

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

if __name__ == "__main__":
    print ("judge the os type with manufacturer")
    for d in getDeviceList():
        print ("->".join(d))
