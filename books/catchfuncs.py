#coding:utf-8
"""存放抓取用的公共函数"""

#--导入所需模块--#
import re
import urllib2

#请求头部
header={}
header['User-Agent']='Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3'
header['Accept-Language'] = 'en-us,en;q=0.7,zh-cn;q=0.3' 
header['Accept-Charset'] = 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'

def getHtml(url):
	"""***得到HTML源代码公用函数--通过python的urllib2模块得到HTML源代码***"""
	req=urllib2.Request(url,headers = header)
	html=urllib2.urlopen(req)
	html=html.read()
	return html

def catchIter(patterns,html):
	"""***抓取公用函数--以正则表达式和需抓取页面的地址为参数，获得页面html源代码；
	并用正则表达式进行匹配，最后得到所有匹配数据的一个迭代器***"""
	p=re.compile(patterns)
	#getdata=re.finditer(p,html)
	getdata=p.finditer(html)
	return getdata
	
def catchSearch(patterns,html):
	"""***抓取公用函数--以正则表达式和需抓取页面的地址为参数，获得页面html源代码；
	并用正则表达式进行匹配，最后得到一个准确的匹配数据***"""
	p=re.compile(patterns)
	#getdata=re.search(p,html)
	getdata=p.search(html)
	return getdata
	
def urlErrorHandler(log,exceptionData):
	"""***捕捉到URLError异常后的处理函数***"""
	if hasattr(exceptionData,'reason'):										#判断错误信息里是否有reason属性，有的话说明是URLError
		eData=exceptionData.reason                                                  #得到错误信息的一个元组，包含错误号和错误原因
		errorInfo='<URLError:' + str(eData[0]) + '--' + eData[1]+'>'
	elif hasattr(exceptionData,'code'):										#判断错误信息里是否有code属性，有的话说明是HTTPError
		eData=exceptionData.code											#得到HTTP错误号
		errorInfo='<HTTPError:' + str(eData) +'>'
	log.errorInfo=errorInfo                                                          		#在日志里记录下错误信息
	log.save()                                                                             	#保存log
	global errorcode												 			#设置全局变量errorcode
	errorcode=1												 				#如果发生错误errorcode为1
	
def getGroup(data,groupName):
	"""从匹配到的HTML数据提取需要的信息"""
	detailData=data.group(groupName).decode('GBK')						#提取数据并转换编码
	return detailData