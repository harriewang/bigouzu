# coding:utf-8
#By Sinomazing
#封装了官方的demo 增加了 异常处理 和 get session还有json解析(eval :-)python万岁)
#[url]http://hi.baidu.com/sinomazing/blog/item/81ca85a20b8cdda4cbefd09b.html[/url] 
from taobaoapi2 import *
import elementtree.ElementTree as ET
import urllib2,math
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from models import SearchLog
from django.db.models import Count

#--构造字典的函数--#
def makedict(**kwargs):
	return kwargs
	
def index(request):
	
	query=request.GET['query']				#获取搜索的关键词
	#if not query:
	#	return HttpResponseRedirect("/")	#如果搜索框中提交的关键词为空，仍然显示首页
	
	#--将用户提交的搜索关键词传递给API部分，并通过解析XML得到搜索结果--#
	url='http://bigouzu.com/search/api/books/q=' + query	#得到真实的url
	url=url.encode('utf-8')										#对url进行转码
	url=urllib2.unquote(url)										#对url进行反引用
	data=urllib2.urlopen(url)										#得到API的所有数据
	root=ET.parse(data).getroot()								#通过ElementTree进行xml解析
	query=root.find('Query').text								#得到Query数据
	booknum=root.find('Num').text									#得到结果个数
	detail=root.findall('Detail')									#得到所有符合搜索的书籍信息的迭代器
	books=[]
	for d in detail:
		info=makedict(title=d.find('book_title').text, author=d.find('book_author').text,
						siteName=d.find('site_name').text, siteUrl=d.find('site_url').text,
						siteLogo=d.find('site_logo').text, youhui=d.find('youhui').text,
						oprice=d.find('old_price').text, price=d.find('price').text,
						buyUrl=d.find('buy_url').text, state=d.find('book_state').text,
						deliverInfo=d.find('deliver_info').text,imgUrl=d.find('book_imgUrl').text,
						)
		books.append(info)										#通过循环得到所有书籍信息的列表
	data.close()													#关闭data对象
	
	#--淘宝关键词搜索--#
	page_size = 20
	try:
	    page = int(request.GET.get('page', '1'))
	except ValueError:
	    page = 1
	itemsget = ItemsGet()
	itemsget.setParams(q=query,page_no=page,page_size=page_size)
	itemsget.fetch()
	taoitems = itemsget.datas
	
	num = itemsget.total_results
	#--分页数据--#
	#pager = bigouzuPager(itemsget.total_results,page_size,page)
	#--保存搜索日志--#
	keyword=query.encode('utf-8')
	ip=request.META['REMOTE_ADDR']
	sessionID=request.session.session_key
	s=SearchLog(keyword=keyword,ip=ip,sessionID=sessionID)
	s.save()
	
	context={'books':books,'query':keyword,'num':num,'taoitems':taoitems}
	return render_to_response('search/result.html',context)

class bigouzuPager(object):
	def __init__(self,total_count, page_size, page):
		self.datas = ''
		if(total_count > page_size):
			total_page = math.ceil( total_count / page_size )
			#-对页码进行规范运算-#
			if page < 1:
				page = 1
			if page > total_count:
				page = total_count
			self.datas.total_count = total_count                                 # 总记录数
			self.datas.page_size = page_size                                 # 分页大小
			self.datas.total_page = total_page                                  # 总页数
			self.datas.first_page  = 1 # 第一页
			#上一页
			if page == 1:
				self.datas.prev_page = 1
			else:
				self.datas.prev_page = (page - 1)
			#下一页
			if  ( page == total_page ) :
				self.datas.next_page = total_page
			else:
				self.datas.next_page = (page + 1)
			self.datas.last_page = total_page                                  # 最后一页
			self.datas.current_page = page                                   # 当前页
			self.datas.aaa = 'aaaa'
			#self.datas.all_pages = [i for i in range(1,total_page)]