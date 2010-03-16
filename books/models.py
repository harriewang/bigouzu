#coding:utf-8
from django.db import models
from djangosphinx.models import SphinxSearch

class SiteInfo(models.Model):
	"""被抓取网站的信息"""
	siteName=models.CharField(max_length=20)  #网站名称
	siteUrl=models.URLField() #网站地址
	startUrl=models.URLField() #抓取的起始地址
	catchName=models.CharField(max_length=100)	#抓取名称
	siteLogo=models.URLField()							#网站Logo地址
	youhui=models.CharField(max_length=200,null=True)	#网站优惠信息
	deliverInfo=models.URLField()	#网站送货信息
	
class TopCategory(models.Model):
	"""抓取得到的一级分类信息"""
	title=models.CharField(max_length=200) #总分类名称
	url=models.URLField() #总分类对应的地址
	updateTime=models.DateTimeField(auto_now=True) #更新时间
	siteId=models.IntegerField() #所属网站ID
	
	
class SubCategory(models.Model):
	"""抓取得到的二级分类信息，是一级分类的子分类"""
	topcategory=models.ForeignKey('TopCategory') #所属一级分类，使用了django的ForeignKey（外键）
	title=models.CharField(max_length=200) #二级分类名称
	url=models.URLField() #二级分类对应的url
	jumpUrl=models.URLField() #跳转后的url地址
	updateTime=models.DateTimeField(auto_now=True) #更新时间
	siteId=models.IntegerField()  #所属网站ID
	
class BookDetail(models.Model):
	"""抓取得到的书籍的具体信息"""
	title=models.CharField(max_length=200)  #书名
	buyUrl=models.URLField()  #书籍购买地址
	price=models.CharField(max_length=20,null=True) #当前网站价格
	oprice=models.CharField(max_length=20,null=True) #原价
	state=models.IntegerField() #货存状态，1代表有货，0代表无货
	caption=models.TextField(null=True) #书籍简介
	imgUrl=models.URLField() #书籍封面小图地址
	bigImgUrl=models.URLField() #书籍封面大图地址
	author=models.CharField(max_length=200,null=True) #作者
	publisher=models.CharField(max_length=200,null=True) #出版社
	date=models.CharField(max_length=200,null=True) #出版日期
	edition=models.CharField(max_length=10,null=True) #版次
	totalPage=models.CharField(max_length=10,null=True) #总页数
	format=models.CharField(max_length=10,null=True) #开本
	isbn=models.CharField(max_length=100,null=True) #ISBN号
	pack=models.CharField(max_length=10,null=True) #装帧
	subCategory=models.CharField(max_length=200) #所属二级分类
	topCategory=models.CharField(max_length=200) #所属一级分类
	updateTime=models.DateTimeField(auto_now=True) #更新时间
	siteId=models.IntegerField() #网站ID
	
	search=SphinxSearch(index='books_bookdetail')
	
class Log(models.Model):
	"""日志模型--记录抓取过程中的相关信息"""
	siteId=models.IntegerField() #记录网站ID
	breakSubId=models.IntegerField()  #记录断点子分类ID
	breakSubTitle=models.CharField(max_length=200) #记录断点子分类名称
	breakPageId=models.IntegerField() #记录断点分页页码
	breakItemId=models.IntegerField() #记录当前页的书籍断点位置
	breakTime=models.DateTimeField(auto_now=True) #记录断点时间
	errorInfo=models.CharField(max_length=200) #记录抓取时发生的错误
	currentEvent=models.CharField(max_length=200) #记录当前事件