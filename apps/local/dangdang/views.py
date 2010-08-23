#coding:utf-8
from books.models import SiteInfo,BookDetail
from django.shortcuts import render_to_response

	
def index(request):		
	return render_to_response('dangdang/index.html',)