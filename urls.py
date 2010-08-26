from django.conf.urls.defaults import *
from django.contrib import admin
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	(r'^taobao/$','taobao.views.index'),
	(r'^yihaodian/$','yihaodian.views.index'),
	(r'^dangdang/$','dangdang.views.index'),
	(r'^joyo/$','joyo.views.index'),
	(r'^bookcatch/addsites/$','books.views.addSite'),
	(r'^bookcatch/editsite_id=(?P<id>\d+)/$','books.views.editSite'),
	(r'^bookcatch/delete_siteid=(?P<id>\d+)/$','books.views.delete'),
	(r'^bookcatch/sitedetail_id=(?P<id>\d+)/$','books.views.siteDetail'),
	(r'^bookcatch/dangdang_categorycatch_siteid=(?P<id>\d+)/$','books.dangdang.categoryCatch'),
	(r'^bookcatch/categorylist_siteid=(?P<id>\d+)/$','books.views.categoryList'),
	(r'^bookcatch/dangdang_detailcatch_siteid=(?P<id>\d+)/$','books.dangdang.bookDetailCatch'),
	(r'^bookcatch/bookdetail_siteid=(?P<siteId>\d+)&subid=(?P<id>\d+)','books.dangdang.bookList'),
	(r'^bookcatch/amazon_categorycatch_siteid=(?P<id>\d+)/$','books.amazon.categoryCatch'),
	(r'^bookcatch/amazon_detailcatch_siteid=(?P<id>\d+)/$','books.amazon.bookDetailCatch'),
	(r'^search.html','search.views.Index'),
	(r'^redir/url/(?P<url>.*)','search.views.redirect'),
	(r'^search/api/books/q=(?P<query>.*)','booksapi.views.searchAPI'),
	(r'^(.*)','main.views.Index'),
  	
	#(r'^$','hello.index'),
	
    # Example:
    # (r'^byb/', include('byb.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
