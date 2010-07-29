# coding:utf-8
import elementtree.ElementTree as ET
import urllib2
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from models import SearchLog
from django.db.models import Count

#--构造字典的函数--#
def makedict(**kwargs):
	return kwargs
	
def Index(request,query):
	
	"""***比购族首页显示及搜索***"""
	hotwords = SearchLog.objects.values('keyword').annotate(keyword_count=Count('keyword')).order_by('-keyword_count')[:30]
	
	try:
		query=request.GET['query']				#获取搜索的关键词
		if not query:
			return HttpResponseRedirect("/")	#如果搜索框中提交的关键词为空，仍然显示首页
		
		#--保存搜索日志--#
		keyword=query.encode('utf-8')
		ip=request.META['REMOTE_ADDR']
		sessionID=request.session.session_key
		s=SearchLog(keyword=keyword,ip=ip,sessionID=sessionID)
		s.save()
		
		#--将用户提交的搜索关键词传递给API部分，并通过解析XML得到搜索结果--#
		
		url='http://bigouzu.com/search/api/books/q=' + query	#得到真实的url
		url=url.encode('utf-8')										#对url进行转码
		url=urllib2.unquote(url)										#对url进行反引用
		data=urllib2.urlopen(url)										#得到API的所有数据
		root=ET.parse(data).getroot()								#通过ElementTree进行xml解析
		query=root.find('Query').text								#得到Query数据
		num=root.find('Num').text									#得到结果个数
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
		context={'books':books,'query':query,'num':num}
		return render_to_response('books/search_result.html',context)
	except:
		#context={'books':list()}
		return render_to_response('index.html',{'hotwords':hotwords})

def keywordSuggest(request,input):
	"""***比购族显示搜索关键词建议***"""
	b=SearchLog.search.query(input)
	import simplejson
	return HttpResponse(simplejson.dumps(input))#simplejson.dumps(b)
    #books=b.order_by('price')
    #return HttpResponse('{"results": []}')#return HttpResponse('{"results": [{"id": "2", "value": "Altman, Alisha", "info":"Buckinghamshire"}, {"id": "3", "value": "Archibald, Janna", "info":"Cambridgeshire"}, {"id": "4", "value": "Auman, Cody", "info":"Cheshire"}]}')

