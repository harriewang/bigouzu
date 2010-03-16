#coding:utf-8
from django import forms

class AddSiteForm(forms.Form):
	siteName=forms.CharField(label="网站名称")
	catchName=forms.CharField(label="抓取名称")
	siteUrl=forms.URLField(label='网站地址')
	startUrl=forms.URLField(label='起始地址')
	siteLogo=forms.URLField(label='Logo地址')
	youhui=forms.CharField(label="优惠信息")
	deliverInfo=forms.URLField(label="送货信息")
	
	