#coding=utf-8

import os
import numpy as np
import matplotlib.pyplot as picture


class Paint:
	def __init__(self,picName):
		self._dir=dir
		self._cpuDoc=[]
		self._memDoc=[]
		self._picName=picName

	def setSaveDir(self,savedir):
		self._saveDir=savedir

	def getPaintDoc(self,dir):
		if not os.path.isdir(dir):
			if dir.find("none")!=-1:
				return

			if dir.find("cpu_info.txt")!=-1:
				self._cpuDoc.append(dir)
			elif dir.find("mem_info.txt")!=-1:
				self._memDoc.append(dir)
			return

		list=os.listdir(dir)
		for t in list:
			if t.startswith('.'):
				continue
			self.getPaintDoc(os.path.join(dir,t))

	def paint(self):
		if not self._saveDir:
			return
		#0表示画cpu曲线
		self.paintCpuOrMem(0)
		#1表示画mem曲线
		self.paintCpuOrMem(1)
		print "-"*20+"finish painting"+"-"*20

	def paintCpuOrMem(self,flag):
		if len(self._cpuDoc)==0 or len(self._memDoc)==0 or len(self._picName)==0:
			return

		if flag==0:
			ylabelName="cpu(%)"
			ylabelLimit=100
			fileList=self._cpuDoc
			saveName="CUP.jpg"
		elif flag==1:
			ylabelName="mem(M)"
			ylabelLimit=250
			fileList=self._memDoc
			saveName="MEM.jpg"
		else:
			print "Paint->paint() error"

		picNo=1
		picture.figure(figsize=(20,30))
		for fileName in fileList:
			x=[]
			y=[]
			file=open(fileName,"r")
			file.readline()
			subPic=picture.subplot(int("42"+str(picNo)))
			picNo+=1
			for line in file:
				data=line.split()
				if not data:
					break
				#将CPU中等于0的值去掉
				if data[1]=="0":
					continue
				#内存的原来单位是K，转换成M
				if flag==1:
					data[1]=str(int(data[1])/1024)

				x.append(data[0])
				y.append(data[1])

			picture.sca(subPic)
			picture.plot(x,y)
			picture.xlabel("time(s)")
			picture.ylabel(ylabelName)
			picture.ylim(0,ylabelLimit)
			picture.title(self._picName[picNo-2])
			file.close()
		# print "picSaveDir=",os.path.join(self._saveDir,saveName)
		picture.savefig(os.path.join(self._saveDir,saveName))
		# picture.show()
