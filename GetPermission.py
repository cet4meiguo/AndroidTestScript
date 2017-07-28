#coding=utf-8

import thread
import threading
from uiautomator import Device

class GetPermission(threading.Thread):
	def __init__(self,deviceId):
		threading.Thread.__init__(self)
		self._deviceId=deviceId
		self._isRunning=True

	def stop(self):
		self._isRunning=False

	def run(self):
		device=Device(self._deviceId)
		print("GetPermission --> "+self._deviceId)
		while self._isRunning:
			try:
				if device(text=u"允许").wait.exists(timeout=2000):
					device(text=u"允许",className="android.widget.Button").click()
					print("允许")
					device(text=u"允许",className="android.widget.Button").click()
					print("允许")
				elif device(text=u"同意").wait.exists(timeout=2000):
					device(text=u"同意",className="android.widget.Button").click()
					print("同意")
					device(text=u"同意",className="android.widget.Button").click()
					print("同意")
				elif device(text=u"继续安装").wait.exists(timeout=2000):
					device(text=u"继续安装",className="android.widget.Button").click()
					print("继续安装")
					device(text=u"继续安装",className="android.widget.Button").click()
					print("继续安装")
			except:
				pass
			# try:
			# 	device(text=u"允许",className="android.widget.Button").click()
			# 	print("允许")
			# 	device(text=u"允许",className="android.widget.Button").click()
			# 	print("允许")
			# except:
			# 	pass
			# if(not self._isRunning):
			# 	print("exit GetPermission")
			# 	break

			# try:
			# 	device(text=u"同意",className="android.widget.Button").click()
			# 	print("同意")
			# 	device(text=u"同意",className="android.widget.Button").click()
			# 	print("同意")
			# except:
			# 	pass
			# if(not self._isRunning):
			# 	print("exit GetPermission")
			# 	break

			# try:
			# 	device(text=u"继续安装",className="android.widget.Button").click()
			# 	print("继续安装")
			# 	device(text=u"继续安装",className="android.widget.Button").click()
			# 	print("继续安装")
			# except:
			# 	pass
			# if(not self._isRunning):
			# 	print("exit GetPermission")
			# 	break