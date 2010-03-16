#coding:utf-8
"""***当当抓取模块，用于抓取当当分类信息，书籍信息***"""

#--需导入信息--#
from models import SiteInfo,TopCategory,SubCategory,BookDetail,Log
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response
from django.core.paginator import Paginator,InvalidPage,EmptyPage          	#导入django的分页机制
from catchfuncs import getHtml,catchIter,catchSearch,urlErrorHandler        	#从catchfuncs导入抓取用的公用函数
from urllib2 import Request, urlopen, URLError                                         	#导入python的urllib2相关函数
from amazonre import *															#从amazonre里导入预编译好的正则表达式
from MySQLdb import DataError,Warning
#import socket

"""
			--已编译正则表达式列表--
	一级分类:			compiledTopPatterns
	二级分类:			compiledSubPatterns
	进口原版书分类:	compiledIOPatterns
	书籍具体信息1:	compiledDetailPatterns_1
	分页:				compiledPagePatterns
	书籍具体信息2:	compiledDetailPatterns_2
	原价:				compiledOpricePatterns
	卓越价:			compiledPricePatterns
	书籍基本信息:		compiledInfoPatterns
	内容简介:			compiledCaptionPatterns
"""


#timeout=60
#socket.setdefaulttimeout(timeout)  #设置超时时间为60秒

def getInfo(t,dic):
	"""***获取书籍基本信息函数***"""
	if t in dic.keys():
		information=dic[t]
	else:
		information=None
	return information

def getPageUrl(url,i):
	"""得到所有分页地址的一个列表
	抓取到的地址：/s/qid=1261566643/ref=sr_pg_2/479-8728444-1200433?ie=UTF8&amp;rs=658445051&amp;bbn=658445051&amp;rh=n%3A658390051%2Cn%3A%21658391051%2Cn%3A658392051%2Cn%3A658445051&amp;page=2
	可访问的地址：' http://www.amazon.cn/s/qid=1261566643/ref=sr_pg_2/479-8728444-1200433?ie=UTF8&rs=658445051&bbn=658445051&rh=n%3A658390051%2Cn%3A%21658391051%2Cn%3A658392051%2Cn%3A658445051&page=2 '
	此函数是为了将以上抓取到的地址转换成可访问的地址
	"""
	url='http://www.amazon.cn' + url[:-1]
	j=str(i)
	u=url + j
	u=u.split('amp;')																					#以'amp;'分割url成为一个列表
	nextUrl=''.join(u)																					#将刚刚分割的url再重新组合，作用是去掉不必要的'amp;'字符
	return nextUrl																						#最后返回一个可以访问的分页地址
	
def categoryCatch(request,id):
	"""***抓取所有一级分离和其子分类***"""
	
	#--得到当前抓取网站相关信息--#
	site=SiteInfo.objects.get(id=id)                                  										#得到当前抓取的站点信息
	log=Log.objects.get(siteId=id)                                   										#得到当前抓取站点的日志Log
	startUrl=site.startUrl                                                 										#得到抓取的起始页地址
	
	#--抓取分类--#
	try:
		topC=compiledTopPatterns.finditer(getHtml(startUrl))                   						#抓取所有一级分类，得到所有一级分类的迭代器
	except URLError,e:                                                               								#如果出现URLError，将错误记录到日志，并返回错误信息和当前事件
		urlErrorHandler(log,e)                                                       								#调用 urlErrorHandler函数处理异常
		log.currentEvent='Catch Category'
		log.save()
		return HttpResponse(log.errorInfo)
	for top in topC:                                                                     							#对上面的迭代器进行循环
		topLink=top.group('TopLink')                                             							#取出一级分类url
		topTitle=top.group('TopTitle')                                           							#取出一级分类标题
		if topTitle !='进口原版':                                                     							#由于卓越的所有分类的进口原版分类url地址错误，所以要把这个分类排除在外，用其他方法抓取
			tc=TopCategory(title=topTitle,url=topLink,siteId=id)       							#将一级分类数据保存到TopCategory的模型中（即：保存到数据库中），siteId为当前抓取站点的id值
			tc.save()
			subHtml=top.group()                                                   							#得到当前一级分类的匹配HTML代码（其中包括每个子分类的列表）
			subC=compiledSubPatterns.finditer(subHtml)                            						#对子分类进行匹配，得到当前一级分类下的所有子分类的一个迭代器
			i=0
			for sub in subC:                                                           							#对子分类迭代器进行循环
				i+=1
				subLink=sub.group('SubLink')                                   							#取出子分类url
				subTitle=sub.group('SubTitle')                                 							#取出子分类名称
				if i !=1:                                                                 							#由于这个迭代器的第一个是一级分类名称，所以应该排除在外
					sc=SubCategory(title=subTitle,url=subLink,topcategory=tc,siteId=id)		#将子分类数据保存到数据库中
					sc.save()
					#--保存成功，将事件记录到日志--#
					log.errorInfo='No Exception Raise'                       								#保存日志错误信息
					log.currentEvent='Save Category Success'           								#保存当前事件
					log.save()
					
	#--抓取“进口原版”分类，由于卓越的所有分类的进口原版分类url地址错误，所以要从其他页面抓取--#
			
	#进口原版的分类地址#		
	IOUrl='http://www.amazon.cn/s/qid=1261309185/ref=sr_nr_n_49?ie=UTF8&rs=658391051&bbn=658391051&rnid=658391051&rh=n%3A658390051%2Cn%3A!658391051%2Cn%3A2045366051'

	try:
		IOData=compiledIOPatterns.finditer(getHtml(IOUrl))                       						#抓取进口原版分类下的子分类，得到一个子分类的迭代器
	except URLError,e:
		urlErrorHandler(log,e)																			#调用 urlErrorHandler函数处理异常
		log.currentEvent='Catch Category'
		return HttpResponse(log.errorInfo)
	tc=TopCategory(title='进口原版',url=IOUrl,siteId=id)                  							#保存‘进口原版’到一级分类数据库中
	tc.save()
	for io in IOData:                                                                     							#对其子分类进行迭代
		subLink=io.group('SubLink')                                                							#取出进口原版子分类地址
		subTitle=io.group('SubTitle')                                              							#取出进口原版子分类名称
		sc=SubCategory(title=subTitle,url=subLink,topcategory=tc,siteId=id)         				#将进口原版保存到数据库中
		sc.save()
		
		#--保存成功，将事件记录到日志--#
		log.errorInfo='No Exception Raise'                                       							#保存日志错误信息
		log.currentEvent='Save Category Success'                           							#保存当前事件
		log.save()
	return HttpResponse('抓取成功，请<a href="/bookcatch/addsites/">返回</a>')   			#抓取完成，返回到站点添加页面
	
def singleBookSave(subcategory,log,bd1,itemId):
	"""***单本书函数：单本书籍的抓取、匹配、最后保存到数据库***"""
	
	#--预先赋值需要的基本信息，用于后面的if判断--#
	P='出版社：'
	E='版本：'
	D='出版日期：'
	I='ISBN：'
	Z='装帧：'
	F='开本：'
	TP='页码：'
	
	#--获取书籍部分信息--#
	imgUrl=bd1.group('ImgUrl')																			#取出封面小图地址
	buyUrl=bd1.group('BuyUrl') 																			#取出购买地址
	title=bd1.group('Title') 																				#取出图书名称
	state=bd1.group('State') 																			#取出货存状态
	#--如果得到的state为‘现在有货。’，则给state赋值1，否则为0--#
	if state=='现在有货。':
		state=1
	else:
		state=0
	#--记录Log--#
	log.currentEvent='Catch bookDetail_2'																#记录当前事件
	log.save()
	
	detailHtml=getHtml(buyUrl)																			#得到当前书籍购买地址对应页面的HTML内容
	bookDetail_2=compiledDetailPatterns_2.search(detailHtml) 										#对当前书籍信息2进行匹配
	if bookDetail_2:
		author=bookDetail_2.group('Author') 															#取出作者
		bigImgUrl=bookDetail_2.group('BigImgUrl') 														#取出封面大图地址
	else:
		author=None
		bigImgUrl='nothing'
	opricedata=compiledOpricePatterns.search(detailHtml)												#匹配原价
	if opricedata:																							#如果匹配到
		oprice=opricedata.group('OPrice')  																#取出原价
	else:																									#如果没有匹配到
		oprice='无'																						#赋值为‘无’
	pricedata=compiledPricePatterns.search(detailHtml)												#匹配卓越价（同原价）
	if pricedata:
		price=pricedata.group('Price')
	else:
		price='无'
	bookDetail_3=compiledInfoPatterns.finditer(detailHtml) 											#对书籍基本信息进行匹配，得到所有基本信息的迭代器
	dic={}  																								#创建一个字典
	for bd3 in bookDetail_3:																				#对基本信息迭代器进行循环
		infoTitle=bd3.group('InfoTitle')
		info=bd3.group('Info')
		dic[infoTitle]=info																					#得到一个包含所有基本信息的字典，后面将取出我们需要的基本信息
	publisher=getInfo(P,dic)																				#调用getInfo函数得到出版社
	date=getInfo(D,dic)																					#调用getInfo函数得到出版日期
	edition=getInfo(E,dic)																				#调用getInfo函数得到版次
	isbn=getInfo(I,dic)																					#调用getInfo函数得到ISBN
	format=getInfo(F,dic)																				#调用getInfo函数得到开本
	pack=getInfo(Z,dic)																					#调用getInfo函数得到装帧
	totalPage=getInfo(TP,dic)																			#调用getInfo函数得到总页数
	captionData=compiledCaptionPatterns.search(detailHtml)  										#匹配内容简介
	if captionData:																							#如果匹配成功
		caption=captionData.group('Caption')  															#取出内容简介
	else:																									#如果匹配不成功
		caption=None  																					#如果内容简介不存在，caption为None
		
	#--保存数据到数据库--#
	bdetail=BookDetail(title=title,buyUrl=buyUrl,price=price,oprice=oprice,
						state=state,caption=caption,imgUrl=imgUrl,bigImgUrl=bigImgUrl,
						author=author,publisher=publisher,date=date,edition=edition,
						totalPage=totalPage,format=format,isbn=isbn,pack=pack,
						subCategory=subcategory.title,topCategory=subcategory.topcategory.title,siteId=subcategory.siteId)
	try:
		bdetail.save()
	except (DataError,Warning):
		pass
	#---记录Log-#
	log.breakItemId=itemId                                                                							#在Log里记录下当前序号
	log.errorInfo='No Exception Raise'                                                 							#书籍保存成功，无异常发生
	log.currentEvent='Save Books Success'                                          							#当前事件为保存书籍成功
	log.save()                                                                                   							#保存Log

def bookDetailCatch(request,id):
	"""***抓取书籍的具体信息，包括书名，作者，价格，购买地址等***"""
	
	#--得到上次抓取的断点信息--#
	log=Log.objects.get(siteId=id)																#取出当前抓取网站的Log
	lastBreakSubId=log.breakSubId																#得到上次抓取的断点子分类id
	lastBreakPageId=log.breakPageId															#得到上次抓取的断点分页页码
	lastBreakItemId=log.breakItemId															#得到上次抓取的分页中的具体断点书籍序号
	subcategory=SubCategory.objects.filter(siteId=id,id__gte=lastBreakSubId)                 	#得到该网站下所有id大于等于断点id的子分类（即从上次断点处开始抓取）
	errorcode=0
	
	#--对所有匹配子分类进行循环、判断、抓取--#
	for c in subcategory:																			#对所有匹配分类进行循环
		log.breakSubId=c.id                                                                                        #在日志里记录当前分类id
		log.breakSubTitle=c.title                                                                     			#在日志里记录当前分类名称
		log.save()                                                                                          			#保存Log
		firstUrl=c.url																				#得到子分类的图书列表第一页地址(后面用于分页)
		
		#--得到下一页的地址，并以此地址做为分页地址的模板，如果下一页存在，则将页数定为100页，否则，说明只有一页，页数定为1--#
		try:
			next=compiledPagePatterns.search(getHtml(firstUrl))  							#抓取下一页分页地址
		except URLError,e:
			urlErrorHandler(log,e)																	#如果出现URLError异常，调用urlErrorHandler函数进行Log记录
			return HttpResponse('Page Exception Raised: %s' % log.errorInfo)                  #由于没有抓取到分页信息，停止抓取，返回错误信息
		if next:																						#如果匹配到下一页
			nextUrl=next.group('Next')															#得到下一页的地址（是一个相对地址，后面将对这个地址进行转换）
			totalPageNum=100                                                                                   #将总页数强制定为100
		else:
			totalPageNum=1																		#如果没有匹配到下一页，则总页数为1
			
		#--开始抓取--#	
		if c.id==lastBreakSubId:																	#判断当前子分类是否是上次断点子分类
			startPage=lastBreakPageId															#如果当前分类是上次断点分类，则从上次断点分页开始抓取，设置起始页为上次断点页码
			for i in range(startPage,totalPageNum+1):											#对所有匹配分页进行循环
				if i==startPage:                                                                    				#判断是否是上次断点分页，如果是，则后面继续判断具体书籍序号
					if i==1:																			
						url=firstUrl																	#如果上次断点分页为第一页，则使用第一页地址firstUrl
					else:
						url=getPageUrl(nextUrl,i)													#如果 i 不等于1，调用getPageUrl函数获取分页地址
					try:
						htmlData=getHtml(url)													#得到当前分页的HTML内容数据
					except URLError,e:															#捕捉URLError异常
						urlErrorHandler(log,e)														#如果捕捉到异常，调用urlErrorHandler函数进行Log记录
					if errorcode==1:																#errocode为1时，说明发生异常，则使用continue跳过本次循环后面的语句，循环到下一页
						continue
					bookinfo=compiledDetailPatterns_1.search(htmlData)						#对书籍信息1进行匹配（用于判断该页是否超出分页范围，如果超出，则匹配结果为None）
					if bookinfo:																	#如果匹配到书籍信息，说明当前页没有超出页码范围
						bookDetail_1=compiledDetailPatterns_1.finditer(htmlData)				#对当前页的书籍信息1进行匹配，得到当前页所有书籍的购买地址等信息的一个迭代器
						itemId=0																	#给当页具体书籍序号初始化
						for bd1 in bookDetail_1:													#对迭代器进行循环，得到每一本书的数据
							itemId+=1                                                                 			#记录下当前书籍序号
							if itemId <= lastBreakItemId:                                      			#如果序号小于等于上次断点序号，跳过后面的语句
								continue
							else:                                                                         			#如果序号大于上次断点序号，进行正常抓取和保存
								try:
									singleBookSave(c,log,bd1,itemId)                        			#执行单本书抓取和保存
								except URLError,e:
									urlErrorHandler(log,e)											#如果捕捉到异常，调用urlErrorHandler函数进行Log记录
								if errorcode==1:													#errorcode为1时，说明发生异常，则使用continue跳过本次循环后面的语句，循环到下一页
									continue
						log.breakItemId=1										  				#当某一分页所有的书籍循环完毕后，立即将Log里的breakItemId置为1
						log.save()
					else:																			#如果bookinfo为None，说明超出页码范围，立即停止分页循环，进行下一个分类的抓取
						break
				else:																				#如果不是上次断点分页，则执行正常抓取
					log.breakPageId=i                                                             			#在Log里记录下当前分页页码
					log.save()
					url=getPageUrl(nextUrl,i)														#调用getPageUrl函数获取分页地址
					try:
						htmlData=getHtml(url)													#得到当前分页的HTML内容数据
					except URLError,e:															#捕捉URLError异常
						urlErrorHandler(log,e)														#如果捕捉到异常，调用urlErrorHandler函数进行Log记录
					if errorcode==1:																#errorcode为1时，说明发生异常，则使用continue跳过本次循环后面的语句，循环到下一页
						continue
					bookinfo=compiledDetailPatterns_1.search(htmlData)						#对书籍信息1进行匹配（用于判断该页是否超出分页范围，如果超出，则匹配结果为None）
					if bookinfo:																	#如果匹配到书籍信息，说明当前页没有超出页码范围
						bookDetail_1=compiledDetailPatterns_1.finditer(htmlData)				#对当前页的书籍信息1进行匹配，得到当前页所有书籍的购买地址等信息的一个迭代器
						itemId=0
						for bd1 in bookDetail_1:													#对迭代器进行循环，得到每一本书的数据
							itemId+=1
							try:
								singleBookSave(c,log,bd1,itemId)                        				#执行单本书抓取和保存
							except URLError,e:
								urlErrorHandler(log,e)												#捕捉到URLError异常后，调用urlErrorHandler函数进行Log记录
							if errorcode==1:														#errocode为1时，说明发生异常，则使用continue跳过本次循环后面的语句，循环到下一本书
								continue
						log.breakItemId=1										  				#当某一分页所有的书籍循环完毕后，立即将Log里的breakItemId置为1
						log.save()
					else:																			#如果匹配分页信息不成功，则超出页码范围，使用break跳出循环，进行下一分类抓取
						break
						
		#---如果当前子分类不是上次断点分类，则从第一页开始正常抓取--#
		else:																						#如果当前子分类不是上次断点分类，则从第一页开始正常抓取
			startPage=1                                                                                			#将起始页置为1
			for i in range(startPage,totalPageNum+1):											#在1-100页进行循环
				log.breakPageId=i  
				log.save()                                                                             			#在Log里记录下当前分页页码
				if i==1:																			#判断当前是否为第一页
					url=firstUrl                                                                					#如果 i 等于1，则说明为第一页，使用第一页地址firstUrl
				else:
					url=getPageUrl(nextUrl,i)														#如果 i 不等于1，调用getPageUrl函数获取分页地址
				try:
					htmlData=getHtml(url)														#得到当前分页的HTML内容数据
				except URLError,e:																#捕捉URLError异常
					urlErrorHandler(log,e)															#如果捕捉到异常，调用urlErrorHandler函数进行Log记录
				if errorcode==1:																	#errocode为1时，说明发生异常，则使用continue跳过本次循环后面的语句，循环到下一页
					continue
				bookinfo=compiledDetailPatterns_1.search(htmlData)							#对书籍信息1进行匹配（用于判断该页是否超出分页范围，如果超出，则匹配结果为None）
				if bookinfo:																		#如果匹配到书籍信息，说明当前页没有超出页码范围
					bookDetail_1=compiledDetailPatterns_1.finditer(htmlData)					#对当前页的书籍信息1进行匹配，得到当前页所有书籍的购买地址等信息的一个迭代器
					itemId=0
					for bd1 in bookDetail_1:														#对迭代器进行循环，得到每一本书的数据
						itemId+=1
						try:
							singleBookSave(c,log,bd1,itemId)                        					#执行单本书抓取和保存
						except URLError,e:														#捕捉到URLError异常后，调用urlErrorHandler函数进行Log记录
							urlErrorHandler(log,e)
						if errorcode==1:															#errocode为1时，说明发生异常，则使用continue跳过本次循环后面的语句，循环到下一本书
							continue
					log.breakItemId=1										  					#当某一分页所有的书籍循环完毕后，立即将Log里的breakItemId置为1
					log.save()
				else:
					break
	return HttpResponse('抓取成功，请<a href="/bookcatch/addsites/">返回</a>')			#抓取完成，返回到添加站点页面
			
"""#对所有分页地址进行循环，进行数据匹配和抓取
		for url in pages:
			htmlData=getHtml(url)
			bookinfo=catchSearch(detailPatterns_1,htmlData)
			if bookinfo:  #判断是否还存在下一页
				bookDetail_1=catchIter(detailPatterns_1,htmlData)  #对当前页的书籍信息1进行匹配，得到购买地址等信息
				#对匹配数据进行循环，得到第一页每一本书的数据
				for bd1 in bookDetail_1:
					imgUrl=bd1.group('ImgUrl') #取出封面小图地址
					buyUrl=bd1.group('BuyUrl') #取出购买地址
					title=bd1.group('Title') #取出图书名称
					state=bd1.group('State') #取出货存状态
					#如果得到的state为‘现在有货。’，则给state赋值1，否则为0
					if state=='现在有货。':
						state=1
					else:
						state=0
					detailHtml=getHtml(buyUrl) #得到当前书籍购买地址对应页面的HTML内容
					bookDetail_2=catchSearch(detailPatterns_2,detailHtml) #对当前书籍信息2进行匹配
					author=bookDetail_2.group('Author') #取出作者
					bigImgUrl=bookDetail_2.group('BigImgUrl') #取出封面大图地址
					opricedata=catchSearch(opricePatterns,detailHtml)
					if opricedata:
						oprice=opricedata.group('OPrice')  #取出原价
					else:
						oprice='nothing'
					pricedata=catchSearch(pricePatterns,detailHtml)
					if pricedata:
						price=pricedata.group('Price')
					else:
						price='nothing'
					bookDetail_3=catchIter(infoPatterns,detailHtml) #对书籍基本信息进行匹配
					dic={}  #创建一个字典
					for bd3 in bookDetail_3:
						infoTitle=bd3.group('InfoTitle')
						info=bd3.group('Info')
						dic[infoTitle]=info
					publisher=getInfo(P,dic)
					date=getInfo(D,dic)
					edition=getInfo(E,dic)
					isbn=getInfo(I,dic)
					format=getInfo(F,dic)
					pack=getInfo(Z,dic)
					totalPage=getInfo(TP,dic)
					captionData=catchSearch(captionPatterns,detailHtml)  #匹配内容简介
					if captionData:
						caption=captionData.group('Caption')  #取出内容简介
					else:
						caption=None  #如果内容简介不存在，caption为None
					bdetail=BookDetail(title=title,buyUrl=buyUrl,price=price,oprice=oprice,
							state=state,caption=caption,imgUrl=imgUrl,bigImgUrl=bigImgUrl,
							author=author,publisher=publisher,date=date,edition=edition,
							totalPage=totalPage,format=format,isbn=isbn,pack=pack,
							subCategory=c.title,topCategory=c.topcategory.title,siteId=id)
					bdetail.save()
			else:
				break
	return HttpResponse('抓取成功，请<a href="/bookcatch/addsite/">返回</a>')
		
		#URLError: <urlopen error (10054, 'Connection reset by peer')>

		#socket.setdefaulttimeout(seconds)   设置超时时间"""
		
		
		
		
		
		
		
		