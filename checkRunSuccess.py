# !/usr/bin/env python -u
# coding=utf-8

import os
import time

class Check(object):
	def __init__(self,runtime,fileDir):
		self._fileDir=fileDir
		self._runtime=runtime
		print("Check->fileDir="+self._fileDir)
		print("runtime="+str(self._runtime))

	def check(self):
		c=os.path.isfile(os.path.join(self._fileDir,"cpu_info.txt"))
		m=os.path.isfile(os.path.join(self._fileDir,"mem_info.txt"))

		if c and m:
			cpu=os.stat(os.path.join(self._fileDir,"cpu_info.txt"))
			mem=os.stat(os.path.join(self._fileDir,"mem_info.txt"))

			cpu_time=int(time.strftime("%M",time.localtime(cpu.st_mtime-cpu.st_birthtime)))
			print("cpu_info.txt_time="+str(cpu_time))
			mem_time=int(time.strftime("%M",time.localtime(mem.st_mtime-mem.st_birthtime)))
			print("mem_info.txt_time="+str(mem_time))
			if cpu_time>=self._runtime and mem_time>=self._runtime:
				return True
			else:
				print("run time is too short,get permission failure")
		else:
			print("Check->check()->file not exists")
		return False

if __name__=="__main__":
	check=Check(10,"./20170725_145341/anchor_single_camera+mic/38083f98")
	print(check.check())


