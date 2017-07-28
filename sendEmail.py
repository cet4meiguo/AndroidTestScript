# coding=utf-8

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.header import Header
import base64
from device_tools import getVersionName

class sendEmail:
	def __init__(self,senderAcount,senderPassword,receiver,attachFilePath):
		self._senderAcount=senderAcount
		self._senderPassword=base64.b64decode(senderPassword)
		self._receiver=receiver
		self._attachFilePath,self._attachFileName=self.compressFile(attachFilePath)
		self._cpu_svg="cpu_info_"+getVersionName("com.zego.livedemo5")+".svg"
		self._mem_svg="mem_info_"+getVersionName("com.zego.livedemo5")+".svg"
		# self.outputHtmlFile()

		print("self._attachFilePath="+self._attachFilePath)
		print("self._attachFileName="+self._attachFileName)
		# print(self._senderAcount)
		# print(self._senderPassword)
		# print(self._receiver)

	def compressFile(self,filePath):
		if filePath.endswith(".zip"):
			fileName=filePath[filePath.rfind("/")+1:]
			return filePath,fileName+".zip"

		fileName=filePath[filePath.rfind("/")+1:]
		# os.popen("rm %s.zip" % fileName)
		print("compress file")
		os.popen("zip -q -r %s.zip %s" % (fileName,fileName))
		filePath=filePath
		return filePath,fileName+".zip"

	def outputHtmlFile(self):		
		htmlHead="""<!DOCTYPE html>
		<html lang="en">
		<body>"""
		htmlTail="""</body>
		</html>"""

		# 输出cpu的html
		file=open(os.path.join(self._attachFilePath,self._cpu_svg),"rb")

		fileContent=htmlHead
		for line in file:
			fileContent+=line
		fileContent+=htmlTail
		file.close()

		html=open(os.path.join(self._attachFilePath,"cpu_info.html"),"w")
		html.write(fileContent)
		html.close()

		# 输出内存的html
		file=open(os.path.join(self._attachFilePath,self._mem_svg),"rb")

		fileContent=htmlHead
		for line in file:
			fileContent+=line
		fileContent+=htmlTail
		file.close()

		html=open(os.path.join(self._attachFilePath,"mem_info.html"),"w")
		html.write(fileContent)
		html.close()

	def send(self):
		message=MIMEMultipart()
		message["From"]=formataddr(["测试程序",self._senderAcount])
		message["To"]=",".join(self._receiver)
		message["Subject"]="Android版LiveDemo5测试报告"

		# msgContent="""
		# <p>邮件发送html格式测试</p>
		# <p><a href="http://www.baidu.com">baidu</a></p>
		# """

		msgContent="""
		<!DOCTYPE html>
		<html lang="en">
		<body>
		"""

		msgContent=msgContent+"<p>Android版的LiveDemo5的测试报告</p><p>以下两张分别为cpu和内存的变化图，浏览器无法显示该图，邮件客户端可以显示</p><p>在邮件客户端下双击附件中的svg图像即可正常打开</p><p>需要更详细的数据请下载附件</p>"

		# 添加cpu的svg图至邮件内容
		file=open(os.path.join(self._attachFilePath,self._cpu_svg),"rb")
		for line in file:
			msgContent+=line
		file.close()
		msgContent+="<p></p>"
		msgContent+="<p></p>"
		# 添加mem的svg图至邮件内容
		file=open(os.path.join(self._attachFilePath,self._mem_svg),"rb")
		for line in file:
			msgContent+=line
		file.close()

		msgContent+="""
		</body>
		</html> 
		"""
		# print(msgContent)
		message.attach(MIMEText(msgContent,"html","utf-8"))

		# 附件 压缩文件
		file=MIMEText(open(self._attachFilePath+".zip","rb").read(),"base64","utf-8")
		file["Content-Type"]="application/octet-stream"
		file["Charset"]="utf-8"
		file["Content-Disposition"]="attachment;filename=%s" % Header(self._attachFileName,"utf-8")
		message.attach(file)

		# 附件 cpu_info.svg
		file=MIMEText(open(os.path.join(self._attachFilePath,self._cpu_svg),"rb").read(),"base64","utf-8")
		file["Content-Type"]="application/octet-stream"
		file["Charset"]="utf-8"
		file["Content-Disposition"]="attachment;filename=%s" % Header(self._cpu_svg,"utf-8")
		message.attach(file)

		# 附件 mem_info.svg
		file=MIMEText(open(os.path.join(self._attachFilePath,self._mem_svg),"rb").read(),"base64","utf-8")
		file["Content-Type"]="application/octet-stream"
		file["Charset"]="utf-8"
		file["Content-Disposition"]="attachment;filename=%s" % Header(self._mem_svg,"utf-8")
		message.attach(file)

		# try:
		# 	os.remove(os.path.join(self._attachFilePath,"cpu_info.html"))
		# 	os.remove(os.path.join(self._attachFilePath,"mem_info.html"))
		# except Exception,e:
		# 	print("sendEmail->*.html not exist")
		# 	print(e)

		try:
			smtpObj=smtplib.SMTP_SSL("smtp.exmail.qq.com",465)
			smtpObj.ehlo()
			smtpObj.login(self._senderAcount,self._senderPassword)
			smtpObj.sendmail(self._senderAcount,self._receiver,message.as_string())
			print("send email success")
		except Exception,e:
			print("sendEmail.py->send()")
			print(e)
		finally:
			smtpObj.close()



if __name__=="__main__":
	print("sendEmail test")
	senderAcount="wujinyong@zego.im"
	senderPassword="V3VqaW55b25nMTIz"
	receiver=["871447603@qq.com","wujinyong@zego.im"]
	send=sendEmail(senderAcount,senderPassword,receiver,"/Users/cier/zegolivedemo/autotest/android/20170726_110224")
	send.send()
