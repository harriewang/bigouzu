#coding:utf-8
"""***当当抓取模块，用于抓取当当分类信息，书籍信息***"""

#--需导入信息--#
from models import SiteInfo,TopCategory,SubCategory,BookDetail,Log
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response
from django.core.paginator import Paginator,InvalidPage,EmptyPage
from catchfuncs import getHtml,catchIter,catchSearch,urlErrorHandler,getGroup   				#从catchfuncs导入抓取用的公用函数
from urllib2 import Request, urlopen, URLError
from MySQLdb import DataError 
from dangdangre import *																			#从dangdangre里导入预编译好的正则表达式

"""
			--已编译正则表达式列表--
	一级分类:			compiledTopPatterns
	二级分类:			compiledSubPatterns
	书籍具体信息1:	compiledDetailPatterns_1
	分页:				compiledPagePatterns
	书籍具体信息2:	compiledDetailPatterns_2
	内容简介:			compiledCaptionPatterns
"""

#--抓取分类信息--#
def categoryCatch(request,id):
	"""***抓取所有一级分类和其子分类***"""
	
	#--得到当前抓取网站相关信息--#
	site=SiteInfo.objects.get(id=id)																	#得到当前抓取的站点信息
	log=Log.objects.get(siteId=id)  																	#得到当前抓取站点的日志Log
	startUrl=site.startUrl  																				#得到抓取的起始页地址
	
	#--开始匹配和抓取--#
	try:
		topC=compiledTopPatterns.finditer(getHtml(startUrl)) 									#调用公共函数catchIter抓取所有一级分类，得到所有一级分类的迭代器
	except URLError,e:																				#如果出现URLError，将错误记录到日志，并返回错误信息和当前事件
		urlErrorHandler(log,e)																			#调用urlErrorHandler函数处理URLError
		log.currentEvent='Catch Category False'													#如果发生异常，则记录事件为'Catch Category False'
		log.save()																						#保存log数据
		return HttpResponse(log.errorInfo)															#返回log信息
	for top in topC:
		topLink=getGroup(top,'TopLink')															#调用getGroup函数，取出一级分类url，并对其转码
		topTitle=getGroup(top,'TopTitle')															#调用getGroup函数，取出一级分类标题，并对其转码
		tc=TopCategory(title=topTitle,url=topLink,siteId=id)										#将一级分类数据保存到TopCategory的模型中，siteId为当前抓取站点的id值
		tc.save()																						#保存一级分类到数据库
		subHtml=top.group()																			#得到当前一级分类的匹配信息（其中包括每个子分类的列表）
		subC=compiledSubPatterns.finditer(subHtml)												#对子分类进行匹配，得到当前一级分类下的所有子分类的一个迭代器
		for sub in subC:																				#对子分类迭代器进行循环
			subLink=getGroup(sub,'SubLink')														#取出子分类url，并对其转码
			subTitle=getGroup(sub,'SubTitle')														#取出子分类标题，并对其转码
			sc=SubCategory(title=subTitle,url=subLink,topcategory=tc,siteId=id)				#将子分类数据赋值给SubCategory模型
			sc.save()																					#保存子分类数据到数据库
			#--记录日志--#
			log.errorInfo='No Exception Raise'
			log.currentEvent='Save Category Success'
			log.save()
	return HttpResponse('抓取成功，请<a href="/bookcatch/addsites/">返回</a>')
	
def getPageUrl(firstUrl,num):
	"""公共函数--得到分页地址，分页地址示例：http://list.book.dangdang.com/01.01.01_P44.htm"""
	page='_P'+str(num)+'.htm'
	url=firstUrl.replace('.htm',page)
	return url
	
def singleBookSave(subcategory,log,b,itemId):
	"""***单本书函数：单本书籍的抓取、匹配、最后保存到数据库***"""
	
	#--得到单本书的信息，并保存到数据库--#
	imgUrl=getGroup(b,'ImgUrl')																		#取出封面小图地址
	buyUrl=getGroup(b,'Url')																			#取出购买地址
	title=b.group('Title')																				#取出书名
	if title:
		title=title.decode('GBK')																		#如果title存在,进行转码
	author=b.group('Author')																		#取出作者
	if author:
		author=author.decode('GBK')																#如果author存在，进行转码
	publisher=b.group('Publisher')																	#取出出版社
	if publisher:
		publisher=publisher.decode('GBK')															#如果publisher存在，进行转码
	date=b.group('Date')																				#取出出版日期
	if date:
		date=date[10:].decode('GBK')																#如果date存在，去掉“出版日期：” 四个字，并转码为UTF-8
	price=getGroup(b,'Price')																		#取出当当价格，并转码
	oprice=getGroup(b,'OPrice')																		#取出原价，并转码
	state=getGroup(b,'State')																		#取出货存状态，并转码
	
	#--如果得到的state为'link_sale'，则有货，赋值为1，否则无货，赋值为0--#
	if state=='link_sale':
		state=1
	else:
		state=0
		
	#--记录当前事件--#
	log.currentEvent='Catch bookDetail_2'
	log.save()
	
	detailHtml=getHtml(buyUrl)																		#得到当前书籍的购买网页数据
	try:
		bookDetail_2=compiledDetailPatterns_2.search(detailHtml)									#抓取书的另一部分信息
		edition=bookDetail_2.group('Edition')[11:].decode('GBK')										#取出版次，去掉“版次：”，并转码
		totalPage=bookDetail_2.group('TPage')[11:].decode('GBK')									#取出总页数，去掉“页数：”，并转码
		format=bookDetail_2.group('Format')[11:].decode('GBK')										#取出开本，去掉“开本：”，并转码
		isbn=bookDetail_2.group('ISBN')[13:].decode('GBK')											#取出ISBN，去掉“ISBN：”，并转码
		pack=bookDetail_2.group('Pack')[11:].decode('GBK')											#取出装帧，去掉“装帧：”，并转码
		bigImgUrl=bookDetail_2.group('BigImgUrl').decode('GBK')										#得到封面大图地址，并转码
		captionData=compiledCaptionPatterns.search(detailHtml)                      					#抓取内容简介，并转码
		if captionData:                                                                            						#如果匹配到简介，则取出
			try:
				caption=captionData.group('Caption').decode('GBK')									#对内容简介进行编码转换
			except UnicodeDecodeError:                                                   						#如果转换编码的过程中捕捉到UnicodeDecodeError，将caption赋值为None
				caption=None
		else: 
			caption=None                                                                        						#如果没有匹配到简介，则赋值为None
	except AttributeError:
		edition='暂无'
		totalPage='暂无'
		format='暂无'
		isbn='暂无'
		pack='暂无'
		bigImgUrl='暂无'
		caption='暂无'
	
	#--保存数据到数据库--#
	bdetail=BookDetail(title=title,buyUrl=buyUrl,price=price,oprice=oprice,
						state=state,caption=caption,imgUrl=imgUrl,bigImgUrl=bigImgUrl,
						author=author,publisher=publisher,date=date,edition=edition,
						totalPage=totalPage,format=format,isbn=isbn,pack=pack,
						subCategory=subcategory.title,topCategory=subcategory.topcategory.title,siteId=subcategory.siteId)
	try:					
		bdetail.save()                                                                              					#保存到数据库
	except DataError:
		pass																							#如果捕捉到DataError，将其忽略，继续抓取
	log.breakItemId=itemId                                                                						#在Log里记录下当前序号
	log.errorInfo='No Exception Raise'                                                 						#书籍保存成功，无异常发生
	log.currentEvent='Save Books Success'                                          						#当前事件为保存书籍成功
	log.save()                                                                                   						#保存Log
				
def bookDetailCatch(request,id):
	"""抓取书籍的具体信息，包括书名，作者，价格，购买地址等"""
	
	#--得到上次抓取的断点信息--#
	log=Log.objects.get(siteId=id)																	#取出当前抓取网站的Log
	lastBreakSubId=log.breakSubId																	#得到上次抓取的断点子分类id
	lastBreakPageId=log.breakPageId																#得到上次抓取的断点分页页码
	lastBreakItemId=log.breakItemId																#得到上次抓取的分页中的具体断点书籍序号
	subcategory=SubCategory.objects.filter(siteId=id,id__gte=lastBreakSubId)					#得到该网站下所有id大于等于断点id的子分类（即从上次断点处开始抓取）
	errorcode=0																						#初始化errorcode
	
	#--对所有匹配子分类进行循环、判断、抓取--#
	for c in subcategory:                                                                                				#对所有匹配分类进行循环
		log.breakSubId=c.id                                                                           				#在日志里记录当前分类id
		log.breakSubTitle=c.title                                                                     				#在日志里记录当前分类名称
		log.save()                                                                                          				#保存Log
		firstUrl=c.url                                                                                      				#得到子分类的图书列表地址(第一页)
		redirectUrl=urlopen(firstUrl).geturl()                                                    				#得到子分类地址重定向后的地址（当当在这里做了重定向）
		
		#--得到总页数--#
		try:
			pageData=compiledPagePatterns.finditer(getHtml(redirectUrl))		                    #抓取列表的分页信息
		except URLError,e:
			urlErrorHandler(log,e)                                                			       				#调用urlErrorHandler函数进行Log记录
			return HttpResponse('Page Exception Raised: %s' % log.errorInfo)     				#由于没有抓取到分页信息，停止抓取，返回错误信息
		try:
			for p in pageData:
				pagenum=p.group('Page')                                                       				#得到当前子分类的总页数
			totalPageNum=int(pagenum)                                                         				#将字符串转化为整型，用于下面的循环
		except NameError:  
			totalPageNum=1                                                                          				#如果不存在第二页，则总页数为1
			
		#--开始抓取--#
		if c.id ==lastBreakSubId:                                                                    				#判断当前子分类是否是上次断点子分类
			startPage=lastBreakPageId                                                           				#如果是，则当前分类的起始页从上次断点分页处开始
			for i in range(startPage,totalPageNum+1):                                     					#对所有匹配分页进行循环
				if i==startPage:                                                                    					#判断是否是上次断点分页，如果是，则后面继续判断具体书籍序号
					if i==1:
						url=redirectUrl                                                          					#如果上次断点分页为第一页，则使用第一页重定向后的地址redirectUrl
					else:
						url=getPageUrl(firstUrl,i)                                           					#如果 i 不等于1，调用getPageUrl函数获取分页地址
					try:
						bookDetail_1=compiledDetailPatterns_1.finditer(getHtml(url))				#抓取书的部分信息,得到当前页所有书籍的一个迭代器
					except URLError,e:																#出现URLError异常后的处理
						urlErrorHandler(log,e)															#调用urlErrorHandler函数处理URLError
					if errorcode==1:																	#如果发生异常，使用continue跳过后面的语句，循环到下一页
						continue
					itemId=0                                                                         				#给当页具体书籍序号初始化
					for b in bookDetail_1:                                                       					#对当前页的所有书籍进行循环
						itemId+=1                                                                 					#记录下当前书籍序号
						if itemId <= lastBreakItemId:                                      					#如果序号小于等于上次断点序号，跳过后面的语句
							continue
						else:																			#如果序号大于上次断点序号，进行正常抓取和保存
							try:
								singleBookSave(c,log,b,itemId)										#执行单本书抓取和保存
							except URLError,e:
								urlErrorHandler(log,e)
							if errorcode==1:															#如果发生异常，使用continue跳过后面的语句，循环到下一本书
								continue
					log.breakItemId=1																#当某一分页所有的书籍循环完毕后，立即将Log里的breakItemId置为1
					log.save()																			#保存到Log
				else:                                                                                      				#如果不是上次断点分页，则执行正常抓取
					log.breakPageId=i                                                             				#在Log里记录下当前分页页码
					log.save()                                                                         				#保存到Log
					url=getPageUrl(firstUrl,i)
					try:
						bookDetail_1=compiledDetailPatterns_1.finditer(getHtml(url))    			#抓取书的部分信息,得到当前页所有书籍的一个迭代器
					except URLError,e:  
						urlErrorHandler(log,e)                                                 					#调用urlErrorHandler函数处理URLError
					if errorcode==1:
						continue
					itemId=0
					for b in bookDetail_1:
						itemId+=1
						try:
							singleBookSave(c,log,b,itemId)                              					#调用singleBookSave函数完成单本书籍的抓取和保存
						except URLError,e:
							urlErrorHandler(log,e)
						if errorcode==1:
							continue
					log.breakItemId=1										  						#当某一分页所有的书籍循环完毕后，立即将Log里的breakItemId置为1
					log.save()												  							#保存到Log
		else:
			startPage=1                                                                                				#如果不是上次断点分类，则从第一页开始
			for i in range(startPage,totalPageNum+1):
				log.breakPageId=i  
				log.save()                                                                             				#在Log里记录下当前分页页码
				if i==1:
					url=redirectUrl                                                                					#如果i为1，则说明为第一页，使用第一页重定向后的地址redirectUrl
				else:
					url=getPageUrl(firstUrl,i)
				try:
					bookDetail_1=compiledDetailPatterns_1.finditer(getHtml(url))         			#抓取书的部分信息，得到当前页下所有书籍的迭代器
				except URLError,e:
					urlErrorHandler(log,e)                                                       					#调用urlErrorHandler函数处理URLError
				if errorcode==1:
					continue
				itemId=0
				for b in bookDetail_1:
					itemId+=1
					try:
						singleBookSave(c,log,b,itemId)                                     					#调用singleBookSave函数完成单本书籍的抓取和保存
					except URLError,e:
						urlErrorHandler(log,e)
					if errorcode==1:
						continue
				log.breakItemId=1
				log.save()
	return HttpResponse('抓取成功，请<a href="/bookcatch/addsites/">返回</a>')
	
def bookDetailUpdate(request,id):
	"""***更新书籍：
	如果抓取得到的书籍已存在，则跳过；
	如果抓取得到的书籍不存在，表示是新书，则将其具体信息保存***"""
	
	#--得到上次抓取的断点信息--#
	log=Log.objects.get(siteId=id)                                                                   #取出当前抓取网站的Log
	lastBreakSubId=log.breakSubId                                                                 #得到上次抓取的断点子分类id
	lastBreakPageId=log.breakPageId                                                              #得到上次抓取的断点分页页码
	lastBreakItemId=log.breakItemId                                                               #得到上次抓取的分页中的具体断点书籍序号
	subcategory=SubCategory.objects.filter(siteId=id,id__gte=lastBreakSubId)   #得到该网站下所有id大于等于断点id的子分类（即从上次断点处开始抓取）
	
	#--对所有匹配分类进行判断和抓取--#
	for c in subcategory:                                                                                #对所有匹配分类进行循环
		log.breakSubId=c.id                                                                           #在日志里记录当前分类id
		log.breakSubTitle=c.title                                                                     #在日志里记录当前分类名称
		log.save()                                                                                          #保存Log
		firstUrl=c.url                                                                                      #得到子分类的图书列表地址(第一页)
		redirectUrl=urlopen(firstUrl).geturl()                                                    #得到子分类地址重定向后的地址（当当在这里做了重定向）
		
		#--得到总页数--#
		pageData=catchIter(pagePatterns,getHtml(redirectUrl))                         #抓取列表的分页信息
		try:
			for p in pageData:
				pagenum=p.group('Page')                                                       #得到当前子分类的总页数
			totalPageNum=int(pagenum)                                                         #将字符串转化为整型，用于下面的循环
		except NameError:  
			totalPageNum=1                                                                          #如果不存在第二页，则总页数为1
			
		#--开始抓取--#
		if c.id ==lastBreakSubId:                                                                    #判断当前子分类是否是上次断点子分类
			startPage=lastBreakPageId                                                           #如果是，则当前分类的起始页从上次断点分页处开始
			for i in range(startPage,totalPageNum+1):                                     #对所有匹配分页进行循环
				if i==startPage:                                                                    #判断是否是上次断点分页，如果是，则后面继续判断具体书籍序号
					if i==1:
						url=redirectUrl                                                          #如果上次断点分页为第一页，则使用第一页重定向后的地址redirectUrl
					else:
						url=getPageUrl(firstUrl,i)                                           #如果 i 不等于1，调用getPageUrl函数获取分页地址
					try:
						bookDetail_1=catchIter(detailPatterns_1,getHtml(url))  #抓取书的部分信息,得到当前页所有书籍的一个迭代器
					except URLError,e:                                                          #出现URLError异常后的处理
						urlErrorHandler(log,e)                                                #调用urlErrorHandler函数处理URLError
					itemId=0                                                                         #给当页具体书籍序号初始化
					for b in bookDetail_1:                                                       #对当前页的所有书籍进行循环
						itemId+=1                                                                 #记录下当前书籍序号
						if itemId <= lastBreakItemId:                                      #如果序号小于等于上次断点序号，跳过后面的语句
							continue
						else:                                                                         #如果序号大于上次断点序号，进行正常抓取和保存
							itemId+=1
							singleBookSave(c,log,b)                                         #执行单本书抓取和保存
				else:                                                                                      #如果不是上次断点分页，则执行正常抓取
					log.breakPageId=i                                                             #在Log里记录下当前分页页码
					log.save()                                                                         #保存到Log
					url=getPageUrl(firstUrl,i)
					try:
						bookDetail_1=catchIter(detailPatterns_1,getHtml(url))    #抓取书的部分信息,得到当前页所有书籍的一个迭代器
					except URLError,e:  
						urlErrorHandler(log,e)                                                 #调用urlErrorHandler函数处理URLError
					itemId=0
					for b in bookDetail_1:
						itemId+=1
						singleBookSave(c,log,b,itemId)                                    #调用singleBookSave函数完成单本书籍的抓取和保存
		else:
			startPage=1                                                                                #如果不是上次断点分类，则从第一页开始
			for i in range(startPage,totalPageNum+1):
				log.breakPageId=i  
				log.save()                                                                             #在Log里记录下当前分页页码
				if i==1:
					url=redirectUrl                                                                #如果i为1，则说明为第一页，使用第一页重定向后的地址redirectUrl
				else:
					url=getPageUrl(firstUrl,i)
				try:
					bookDetail_1=catchIter(detailPatterns_1,getHtml(url))         #抓取书的部分信息，得到当前页下所有书籍的迭代器
				except URLError,e:
					urlErrorHandler(log,e)                                                       #调用urlErrorHandler函数处理URLError
				itemId=0
				for b in bookDetail_1:
					itemId+=1
					singleBookSave(c,log,b)
					log.breakItemId=itemId
					log.save()
	return HttpResponse('抓取成功，请<a href="/bookcatch/addsite/">返回</a>')
	
def bookList(request,siteId,id):
	site=SiteInfo.objects.get(id=siteId)
	sub=SubCategory.objects.get(id=id)
	top=sub.topcategory
	booklist=BookDetail.objects.filter(siteId=siteId,subCategory=sub.title)
	paginator=Paginator(booklist,20)  # 20 objects per page
	# Make sure page request is an int. If not, deliver first page.
	try:
		page=int(request.GET.get('page','1'))
	except ValueError:
		page=1
	# If page request is out of range, deliver last page of results.
	try:
		pagecase=paginator.page(page)
	except (EmptyPage,InvalidPage):
		pagecase=paginator.page(paginator.num_pages)
	return render_to_response('books/booklist.html',{'pagecase':pagecase,'site':site,'sub':sub,'top':top})
	
"""try:
					bd=BookDetail.objects.get(siteId=id,title=title,buyUrl=buyUrl)
					bd.title=title
					bd.buyUrl=buyUrl
					bd.price=price
					bd.oprice=oprice
					bd.state=state
					bd.caption=caption
					bd.imgUrl=imgUrl
					bd.bigImgUrl=bigImgUrl
					bd.author=author
					bd.publisher=publisher
					bd.date=date
					bd.edition=edition
					bd.totalPage=totalPage
					bd.format=format
					bd.isbn=isbn
					bd.pack=pack
					bd.subCategory=c.title
					bd.topCategory=c.topCategory.title
					bd.siteId=id
					bd.save()
				except ObjectDoesNotExsit:
					bdetail=BookDetail(title=title,buyUrl=buyUrl,price=price,oprice=oprice,
							state=state,caption=caption,imgUrl=imgUrl,bigImgUrl=bigImgUrl,
							author=author,publisher=publisher,date=date,edition=edition,
							totalPage=totalPage,format=format,isbn=isbn,pack=pack,
							subCategory=c.title,topCategory=c.topcategory.title,siteId=id)
					bdetail.save()"""
	