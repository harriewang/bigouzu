# coding:utf-8
from taobaoapi2 import *
import elementtree.ElementTree as ET
import urllib2
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from search.models import SearchLog
from django.db.models import Count
	
def index(request):
	"""***比购族首页热门关键词***"""
	hotwords = SearchLog.objects.values('keyword').annotate(keyword_count=Count('keyword')).order_by('-keyword_count')[:25]
	return render_to_response('index.html',{'hotwords':hotwords})

def redirect(request):
	url=request.GET['url']
	if url:
		return HttpResponseRedirect(url)
	else:
		return HttpResponseRedirect("/")