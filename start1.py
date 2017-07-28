#!/usr/bin/env python -u
#coding=utf-8

'''
the test will start here
'''

import os
import shutil
import argparse
import time
from device_tools import getDeviceList
from device_tools import getDeviceNameAndModel
from device_tools import setScreenAlwaysOn
from device_tools import lockDevicesScreen
from tester1 import Tester
from paint import Paint
from PaintSVG import PaintSVG
from GetPermission import GetPermission
from sendEmail import sendEmail
from checkRunSuccess import Check
from getLatestApkFromShare import get_latest_apk_from_share

enters={
"setting": "com.zego.livedemo5.testSettings",
"performance":None
}
resultDir=(
	"anchor_single_camera+mic",
	"anchor_single_mic",
	"anchor_single_camera",
	"anchor_twoAnchorConnect",
	"anchor_ThreeAnchorConnect",
	"client_justEnterRoom",
	"client_onlyCamera",
	"client_onlyMic",
	"settingTest"
	)
testPkg=(
	"com.zego.livedemo5.anchorSingleCameraMic",
	"com.zego.livedemo5.anchorSingleMic",
	"com.zego.livedemo5.anchorSingleCamera",
	"com.zego.livedemo5.anchorStartMoreAnchorRoom",
	"com.zego.livedemo5.anchorConnectToMoreAnchorRoom",
	"com.zego.livedemo5.anchorSingleCameraMic",
	"com.zego.livedemo5.anchorSingleCamera",
	"com.zego.livedemo5.anchorSingleMic"
	)


#scan the current folder to finder targetApk and testApk
def _scan():
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

# 结束获取权限的线程
def clearGetPermission(permissionThread):
	print("enter clearGetPermission")
	per=permissionThread[0]
	for per in permissionThread:
		per.stop()
		# per.join()
	del permissionThread[:]
	print("len(permissionThread)="+str(len(permissionThread)))
	print("out clearGetPermission")

# 开启获取权限的线程
def startGetPermission(permissionThread,devices):
	for device in devices:
		per=GetPermission(device[0])
		per.start()
		permissionThread.append(per)

def removeExistFile(path):
	if os.path.exists(path):
		shutil.rmtree(path,True)

if __name__=="__main__":
	print ("start1,__main__")
	if __name__!="__main__":
		os.chdir(os.path.dirname(__file__))
		
	# get_latest_apk_from_share()

	parse=argparse.ArgumentParser();

	parse.add_argument('-a','--target',action='store',type=str,help="the apk path that will be test,default is current directory")
	parse.add_argument('-t','--test',action="store",type=str,help="the test apk path,default is current directory")
	parse.add_argument('-m','--mode',action="store",type=str,choices=enters.keys(),help="the test mode,default is None,will exit")

	args=parse.parse_args();
	targetApk=args.target
	testApk=args.test
	enterPkg=enters[args.mode]
	# print ("enterPkg=" + enterPkg)

	if targetApk==None and testApk==None:
		targetApk,testApk=_scan()

	beginTime=time.strftime("%Y%m%d_%H%M%S",time.localtime())
	scriptRoot=os.path.split(os.path.realpath(__file__))[0]
	resultPath=scriptRoot

	try:
		resultPath=os.path.join(scriptRoot,beginTime)
		print ("resultPath="+resultPath)
		os.mkdir(resultPath)
	except Exception,e:
		resultPath=scriptRoot
		print (e)

	# print "beginTime=",beginTime," scriptRoot="+scriptRoot," resultRoot=",resultPath

	devices=getDeviceList()
	print ("==="*5+" device list "+"==="*5)
	print (os.linesep.join(['->'.join(device) for device in devices]))
	print ("==="*14)

	permissionThread=[]
	
	threads=[]
	local_port=5555
	collectDeviceId=devices[0][0]
	runtime=2
	setScreenAlwaysOn()

	# 重定向终端输出至文件
	# file=open("123.txt","w")
	# sys.stdout=file
	if args.mode=='performance':
		# # 主播端 单麦
		if len(devices)>=1:
			startGetPermission(permissionThread,devices)
			# time.sleep(10)
			for i in range(0,1):
				print ("targetApk=",targetApk," testApk=",testApk," testPkg=",testPkg[i])
				
				check=Check(runtime+2,os.path.join(resultPath,resultDir[i],collectDeviceId))
				while not check.check():
					removeExistFile(os.path.join(resultPath,resultDir[i]))
					tester=Tester(targetApk,testApk,testPkg[i])
					tester.setDevice(collectDeviceId,local_port)
					os.mkdir(os.path.join(resultPath,resultDir[i]))
					tester.setOutputPath(os.path.join(resultPath,resultDir[i]))
					t=tester.doRun()
					threads.append(t)

					t.join()

				print ("-----"*5+" end "+resultDir[i]+" "+"-----"*5)

			del threads[:]
			clearGetPermission(permissionThread)
		else:
			print("没有手机")

		# 两个主播连麦
		devices=getDeviceList()
		if len(devices)>=2:
			startGetPermission(permissionThread,devices)
			# time.sleep(10)
			print ("targetApk=",targetApk," testApk=",testApk," testPkg=",testPkg[3])
			check=Check(runtime+2,os.path.join(resultPath,resultDir[3],collectDeviceId+"_anchor"))
			while not check.check():
				removeExistFile(os.path.join(resultPath,resultDir[3]))
				tester=Tester(targetApk,testApk,testPkg[3])
				tester.setDevice(collectDeviceId,local_port)
				os.mkdir(os.path.join(resultPath,resultDir[3]))
				tester.setOutputPath(os.path.join(resultPath,resultDir[3]),"_anchor")
				t=tester.doRun()
				threads.append(t)
				local_port+=1

				time.sleep(120)#两分钟之后再开启连麦
				print ("targetApk=",targetApk," testApk=",testApk," testPkg=",testPkg[4])
				tester=Tester(targetApk,testApk,testPkg[4])
				tester.setDevice(devices[1][0],local_port)
				tester.setOutputPath(os.path.join(resultPath,resultDir[3]),"_otherAnchor_none")
				t=tester.doRun()
				threads.append(t)

				while True:
					for thread in threads:
						if thread.is_alive()==False:
							threads.remove(thread)
					if len(threads)==0:
						break
			clearGetPermission(permissionThread)
			print ("-----"*5+" end "+resultDir[3]+" "+"-----"*5)
		else:
			print("小于两个手机，无法两个主播连麦")

		# # 三个主播连麦
		devices=getDeviceList()
		if len(devices)>=3:
			startGetPermission(permissionThread,devices)
			# time.sleep(10)
			print ("targetApk=",targetApk," testApk=",testApk," testPkg=",testPkg[3])
			check=Check(runtime+2,os.path.join(resultPath,resultDir[4],collectDeviceId+"_anchor"))
			while not check.check():
				removeExistFile(os.path.join(resultPath,resultDir[4]))
				tester=Tester(targetApk,testApk,testPkg[3])
				tester.setDevice(collectDeviceId,local_port)
				os.mkdir(os.path.join(resultPath,resultDir[4]))
				tester.setOutputPath(os.path.join(resultPath,resultDir[4]),"_anchor")
				t=tester.doRun()
				threads.append(t)
				local_port+=1

				time.sleep(120)#两分钟之后再开启连麦
				print ("targetApk=",targetApk," testApk=",testApk," testPkg=",testPkg[4])
				tester=Tester(targetApk,testApk,testPkg[4])
				tester.setDevice(devices[1][0],local_port)
				tester.setOutputPath(os.path.join(resultPath,resultDir[4]),"_otherAnchor_none")
				t=tester.doRun()
				threads.append(t)
				local_port+=1

				print ("targetApk=",targetApk," testApk=",testApk," testPkg=",testPkg[4])
				tester=Tester(targetApk,testApk,testPkg[4])
				tester.setDevice(devices[2][0],local_port)
				tester.setOutputPath(os.path.join(resultPath,resultDir[4]),"_otherAnchor_none")
				t=tester.doRun()
				threads.append(t)
				local_port+=1

				while True:
					for thread in threads:
						if thread.is_alive()==False:
							threads.remove(thread)
					if len(threads)==0:
						break
			clearGetPermission(permissionThread)
			print ("-----"*5+" end "+resultDir[4]+" "+"-----"*5)
		else:
			print("小于3个手机，无法进行3个主播连麦")

		# 客户端测试
		devices=getDeviceList()
		if len(devices)>=2:
			startGetPermission(permissionThread,devices)
			# time.sleep(10)
			for i in range(5,8):
				check=Check(runtime,os.path.join(resultPath,resultDir[i],collectDeviceId+"_client"))
				while not check.check():
					removeExistFile(os.path.join(resultPath,resultDir[i]))
					tester=Tester(targetApk,testApk,testPkg[i])
					tester.setDevice(devices[1][0],local_port)
					os.mkdir(os.path.join(resultPath,resultDir[i]))
					tester.setOutputPath(os.path.join(resultPath,resultDir[i]),"_anchor_none")
					t=tester.doRun()
					threads.append(t)
					local_port+=1

					time.sleep(120)#客户端在两分钟之后再进入
					joinRoomPkg="com.zego.livedemo5.clientJoinPublishRoom"
					tester=Tester(targetApk,testApk,joinRoomPkg)
					tester.setDevice(collectDeviceId,local_port)
					tester.setOutputPath(os.path.join(resultPath,resultDir[i]),"_client")
					t=tester.doRun()
					threads.append(t)

					while True:
						for thread in threads:
							if thread.is_alive()==False:
								threads.remove(thread)
						if len(threads)==0:
							break

					print ("-----"*5+" end "+resultDir[i]+" "+"-----"*5)
			clearGetPermission(permissionThread)

		else:
			print("小于两个手机，无法测试客户端")

		# 绘图 JPG
		# painter=Paint(resultDir)
		# painter.setSaveDir(resultPath)
		# painter.getPaintDoc(resultPath)
		# painter.paint()
		# 绘图 SVG
		deviceNameAndModel=getDeviceNameAndModel()
		paintSvg=PaintSVG(resultPath,deviceNameAndModel)
		paintSvg.paint()

		# 发送邮件
		senderAcount="wujinyong@zego.im"
		senderPassword="V3VqaW55b25nMTIz"
		receiver=["wujinyong@zego.im","randyqiu@zego.im",
		"markwu@zego.im","uei.zeng@zego.im"]
		send=sendEmail(senderAcount,senderPassword,receiver,resultPath)
		send.send()

		# lockDevicesScreen()

		

	elif args.mode=='setting':
		for device in devices:
			tester=Tester(targetApk,testApk,enterPkg)
			tester.setDevice(device[0],local_port)
			os.mkdir(os.path.join(resultPath,resultDir[8]))
			tester.setOutputPath(os.path.join(resultPath,resultDir[8]))
			t=tester.doRun()
			threads.append(t)
			local_port+=1

	for t in threads:
		print ("call %s's join" % t.getName())
		t.join()
