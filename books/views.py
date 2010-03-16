#coding: utf-8
from models import SiteInfo,TopCategory,SubCategory,BookDetail,Log
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response
from forms import AddSiteForm

def addSite(request):
	"""添加需要抓取的网站，包括网站名称，地址，抓取的起始地址"""
	if request.method=='POST':    #如果request的方法为POST，即有表单提交
		form=AddSiteForm(request.POST)   
		if form.is_valid():  #验证提交的数据，如果通过验证，往下执行
			siteName=form.cleaned_data['siteName']  #网站名称
			siteUrl=form.cleaned_data['siteUrl']  #网站地址
			startUrl=form.cleaned_data['startUrl']   #抓取的起始URL
			site=SiteInfo(siteName=siteName,siteUrl=siteUrl,startUrl=startUrl)  
			site.save()  #保存到数据库
			#日志初始化#
			siteId=site.id   #记录当前网站id
			breakSubId='1'  #初始化断点分类id为1
			breakSubTitle='nothing'  #初始化断点分类名称为nonthing
			breakPageId=1  #初始化断点分页为1
			breakItemId=0  #初始化断点书籍序号为1
			errorInfo='No Exception Raise'  #初始化错误信息为'No Exception Raise'
			currentEvent='Log Initialization'  #初始化当前时间为'Log Initialization'
			log=Log(siteId=siteId,breakSubId=breakSubId,breakSubTitle=breakSubTitle,
					breakPageId=breakPageId,breakItemId=breakItemId,errorInfo=errorInfo,currentEvent=currentEvent)
			log.save()
			return HttpResponse('网站信息添加成功，日志初始化成功，请<a href="/bookcatch/addsites/">返回</a>')  #显示添加成功信息，提供返回到添加页面
	else:
		form=AddSiteForm()  #如果无表单提交，显示空白表单
	allsite=SiteInfo.objects.all() #得到所有的siteInfo
	alllog=Log.objects.all() #得到所有Log
	return render_to_response('books/addsite.html',{'allsite':allsite,'form':form,'alllog':alllog})  #返回经过渲染的addsite.html
	
def editSite(request,id):
	s=SiteInfo.objects.get(id=id)
	log=Log.objects.get(siteId=id)
	current_data = {'siteName':s.siteName,'catchName':s.catchName,'siteUrl':s.siteUrl,
						'startUrl':s.startUrl,'siteLogo':s.siteLogo,'youhui':s.youhui,
						'deliverInfo':s.deliverInfo}
	form =AddSiteForm(initial=current_data)
	if request.method=='POST':
		form=AddSiteForm(request.POST)
		if form.is_valid():
			s.siteName=form.cleaned_data['siteName']
			s.catchName=form.cleaned_data['catchName']
			s.siteUrl=form.cleaned_data['siteUrl']
			s.startUrl=form.cleaned_data['startUrl']
			s.siteLogo=form.cleaned_data['siteLogo']
			s.youhui=form.cleaned_data['youhui']
			s.deliverInfo=form.cleaned_data['deliverInfo']
			s.save()
			
			#--修改日志--#
			log.currentEvent='Edit SiteInfo'
			log.save()
			return HttpResponse('网站信息修改成功，请<a href="/bookcatch/addsites">返回</a>')
	else:
		return render_to_response('books/editsite.html',{'form':form})

def siteDetail(request,id):
	s=SiteInfo.objects.get(id=id)
	log=Log.objects.get(siteId=id)
	return render_to_response('books/sitedetail.html',{'site':s,'log':log})

def categoryList(request,id):
	"""显示所有分类"""
	site=SiteInfo.objects.get(id=id)
	top=TopCategory.objects.filter(siteId=id)
	sub=SubCategory.objects.filter(siteId=id)
	return render_to_response('books/categorylist.html',{'site':site,'top':top,'sub':sub})

def delete(request,id):
	top=TopCategory.objects.filter(siteId=id)
	top.delete()
	sub=SubCategory.objects.filter(siteId=id)
	sub.delete()
	books=BookDetail.objects.filter(siteId=id)
	if books:
		books.delete()
	return HttpResponseRedirect('/bookcatch/addsites/')