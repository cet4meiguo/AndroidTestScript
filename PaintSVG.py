# coding=utf-8

import pygal
import os
from device_tools import getVersionName

name={
	"anchor_single_camera+mic":u"主播端-单麦-麦+相机",
	"anchor_single_mic":u"主播端-单麦-麦",
	"anchor_single_camera":u"主播端-单麦-相机",
	"anchor_twoAnchorConnect":u"主播端-双麦-麦+相机",
	"anchor_ThreeAnchorConnect":u"主播端-三麦-麦+相机",
	"client_justEnterRoom":u"客户端-单麦-麦+相机",
	"client_onlyCamera":u"客户端-单麦-相机",
	"client_onlyMic":u"客户端-单麦-麦",
	"settingTest":u"设置"
}

# 画SVG图
class PaintSVG:
	def __init__(self,saveDir,deviceNameAndModel):
		self._saveDir=saveDir
		self._cpuDoc=[]
		self._memDoc=[]
		self._deviceNameAndModel=deviceNameAndModel
		self.getPaintDoc(self._saveDir)

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
		self._cpu_svg_saveName="cpu_info_"+getVersionName("com.zego.livedemo5")+".svg"
		self.paintChart(self._cpu_svg_saveName,self._cpuDoc,yTitle=u"CPU使用(%)")
		self._mem_svg_saveName="mem_info_"+getVersionName("com.zego.livedemo5")+".svg"
		self.paintChart(self._mem_svg_saveName,self._memDoc,yTitle=u"内存使用(MB)")

	def paintChart(self,saveName,paintDoc,yTitle="use"):
		if not paintDoc:
			return
		line_chart=pygal.Line(show_dots=False,x_label_rotation=1,show_minor_x_labels=False,
			x_title=u"时间(s)",y_title=yTitle,width=1200,
			truncate_legend=-1,legend_at_bottom=True)
		line_chart.title=saveName[:saveName.rfind("_")]

		x,y=self.getData(paintDoc[0])
		line_chart.x_labels=x
		line_chart.x_labels_major=range(x[0],x[-1],60)
		line_chart.add(self.getLineName(paintDoc[0]),y)
		for i in range(1,len(paintDoc)):
			x,y=self.getData(paintDoc[i])
			line_chart.add(self.getLineName(paintDoc[i]),y)

		line_chart.render_to_file(os.path.join(self._saveDir,saveName),encoding='utf-8')

	def getLineName(self,filePath):
		start=filePath.index("/",len(self._saveDir)-1)+1
		# end=filePath.rfind("/")
		end=filePath.index("/",len(self._saveDir)+1)
		start1=filePath.index("/",len(self._saveDir)+1)+1
		end1=filePath.rfind("/")
		if filePath.rfind("_anchor")>start1 and filePath.rfind("none")==-1:
			end1=filePath.rfind("_anchor")
		if filePath.rfind("_client")>start1 and filePath.rfind("none")==-1:
			end1=filePath.rfind("_client")
		try:
			phone=self._deviceNameAndModel[filePath[start1:end1]]
		except:
			print("error aaaaaaaa")
		return name[filePath[start:end]]+"-"+phone

	def getData(self,filePath):
		x=[]
		y=[]
		file=open(filePath,"r")
		file.readline()
		isMem=False
		if filePath.find("mem_info.txt")!=-1:
			isMem=True
		for line in file:
			data=line.split()
			if not data:
				break
			if data[1]=="0":
				continue
			if isMem:
				data[1]=str(int(data[1])/1024)

			x.append(int(data[0]))
			y.append(int(data[1]))
		return x,y

if __name__=="__main__":
	print("test PaintSVG")