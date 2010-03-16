#coding:utf-8
from django.db import models

class SearchLog(models.Model):
	"""搜索日志"""
	keyword=models.CharField(max_length=255) 			#搜索的关键词
	ip=models.IPAddressField()								#搜索者的IP地址
	sessionID=models.CharField(max_length=255)			#搜索者搜索时产生的sessionID
	addtime=models.DateTimeField(auto_now_add=True)	#搜索的时间
	
	def __unicode__(self):
		return self.keyword
		
	class Meta:
		ordering=['addtime']		#按照搜索时间排序
