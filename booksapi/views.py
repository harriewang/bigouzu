#coding:utf-8
from books.models import SiteInfo,BookDetail
from django.shortcuts import render_to_response

	
def searchAPI(request,query):
	"""***生成查询集的API,用xml模板进行渲染，将返回结果存储到文件中***"""
	
	allsites=SiteInfo.objects.all()
	try:
		b=BookDetail.search.query(query)
		books=b.order_by('price')												#按价格排序
		#--排除重复项目--#
		results=[]
		same=[]
		for book in books:
			(title,siteId) =(book.title,book.siteId)
			s=(title,siteId)
			if s in same:
				continue
			else:
				same.append(s)
				results.append(book)
		#--context--#
		context = { 'books': results,'query': query,'num':len(results),'search_meta':b._sphinx,'allsites':allsites}
	except:
		context={'books':list(),'allsites':allsites}
		
	return render_to_response('books/search.xml',context)