#coding:utf-8
"""***对所有当当的正则表达式进行预编译，供导入给抓取模块用***"""

from re import compile

#一级分类正则表达式#
topPatterns='<h3>[\s]*?'+\
		'<a href=\'(?P<TopLink>.*\') target=.*>(?P<TopTitle>.*)</a>[\s]*?'+\
		'</h3>[\s]*?'+\
		'<ul>[\s]*?'+\
		'(<li><a href=".*" target=.*>.*</a></li>[\s]*?)+'+\
		'</ul>'
compiledTopPatterns=compile(topPatterns)							#对其进行预编译

#二级分类正则表达式#
subPatterns='<li><a href="(?P<SubLink>.*)" target=.*>(?P<SubTitle>.*)</a></li>'
compiledSubPatterns=compile(subPatterns)							#对其进行预编译

#书籍具体信息1：书名，作者，出版社，出版日期，原价，当当价#
detailPatterns_1='<span class="list_r_list_book">[\s]*?'+\
		'<a name="link_prd_img" href=".*" target="_blank"><img src="(?P<ImgUrl>.*)"  border="0"/></a>[\s]*?'+\
		'</span>[\s]*?'+\
		'</div>[\s]*?'+\
		'<div class="list_book_right">[\s]*?'+\
		'<h2>[\s]*?'+\
		'<a name="link_prd_name" href="(?P<Url>.*)" target="_blank">(?P<Title>.*)</a>[\s]*?'+\
		'</h2>[\s]*?'+\
		'<h3>[\s]*?'+\
		'.*?</h3>[\s]*?'+\
		'(<h4 class="list_r_list_h4">.*<a href=".*" title=".*"  target="_blank" name=".{4}">(?P<Author>.*?)</a>.*?</h4>[\s]*?)?'+\
		'(<h4>.*<a href=".*" title=".*" target="_blank" name=".{6}">(?P<Publisher>.*?)</a>[\s\S]*?)?'+\
		'(<h4>(?P<Date>.*)</h4>[\s]*?)?'+\
		'<h5>[\s\S]*?</h5>[\s]*?'+\
		'<div class="clear"></div>[\s]*?'+\
		'<h6><span class="del">\xa3\xa4(?P<OPrice>.*)</span>.*?<span class="red">\xa3\xa4(?P<Price>.*)</span>.*</h6>[\s]*?'+\
		'	<span class="list_r_list_button">[\s]*?'+\
		'<a name=\'(?P<State>.*?)\' href=.*?><img src=.* title=.*/></a>'
compiledDetailPatterns_1=compile(detailPatterns_1)					#对其进行预编译
          
#分页#
pagePatterns='<a name="link_page"  href=".*?"  class=".*">(?P<Page>\d{1,2})</a>'
compiledPagePatterns=compile(pagePatterns)							#对其进行预编译

#书籍具体信息2：版次，总页数，开本，ISBN，装帧#
detailPatterns_2='<div class="book_left"><div class="book_pic">[\s]*?'+\
				'<a href=".*" name="bigpicture_bk"><img src="(?P<BigImgUrl>.*)"  id="img_show_prd"/></a>[\s]*?'+\
				'</div>[\s]*?<input type="hidden" id="hid_largepictureurl"/>[\s]*?'+\
				'</div>[\s]*?'+\
				'<div class="book_right">[\s]*?'+\
				'<div id=.* >.*</div>[\s]*?'+\
				'<div id=.*>.*</div>[\s]*?'+\
				'<ul >[\s]*?'+\
				'<li>.*</li>[\s]*?'+\
				'<li>.*</li>[\s]*?'+\
				'<li>(?P<Edition>.*)</li>[\s]*?'+\
				'<li>(?P<TPage>.*)</li>[\s]*?'+\
				'<li>.*</li>[\s]*?'+\
				'<li>(?P<Format>.*)</li>[\s]*?'+\
				'<li>.*</li>[\s]*?'+\
				'<li>.*</li>[\s]*?'+\
				'<li>(?P<ISBN>.*)</li>[\s]*?'+\
				'<li>(?P<Pack>.*)</li>[\s]*?'+\
				'</ul>'
compiledDetailPatterns_2=compile(detailPatterns_2)					#对其进行预编译

#内容简介#
captionPatterns='<h2 class="black14"><img src="images/bg_point1.gif" align="absmiddle" /> \xc4\xda\xc8\xdd\xbc\xf2\xbd\xe9</h2> <div class="zhengwen">(?P<Caption>[\S\s]*?)</div>'
compiledCaptionPatterns=compile(captionPatterns)					#对其进行预编译

