#coding:utf-8
"""***对所有当当的正则表达式进行预编译，供导入给抓取模块用***"""

from re import compile

#一级分类#
topPatterns='<div id="name"><a href="(?P<TopLink>.*)">(?P<TopTitle>.*)</a></div>[\s]*?'+\
				'(<a href=".*?">.*?</a>[\s]*?&nbsp;\|[\s]*?)+'+\
				'<a href=".*">.*</a>'
compiledTopPatterns=compile(topPatterns)							#对其进行预编译

#子分类#
subPatterns='<a href="(?P<SubLink>.*)">(?P<SubTitle>.*)</a>'
compiledSubPatterns=compile(subPatterns)							#对其进行预编译

#进口原版书分类#
IOPatterns='<li style="margin-left: 6px;"><a href="(?P<SubLink>.*)" ><span class="refinementLink">(?P<SubTitle>.*)</span><span  class="narrowValue">.*?</span></a></li>'
compiledIOPatterns=compile(IOPatterns)

#书籍具体信息1：书名，购买地址，封面小图地址，是否有货#
detailPatterns_1='<div class="productImage"><a href=".*">[\s\S]*?'+\
			'src="(?P<ImgUrl>.*)" class="" border="0" alt=".*"  width="\d*" height="\d*"/> </a></div>[\s]*?'+\
			'<div class="productData">[\s]*?'+\
			'<div class="productTitle"><a href="(?P<BuyUrl>.*)">(?P<Title>.*)</a>[\S\s]*?'+\
			'<div class="fastTrack" style="margin: 4px 0px 2px 0px;">(?P<State>.*)</div>'
compiledDetailPatterns_1=compile(detailPatterns_1)					#对其进行预编译
          
#分页#
pagePatterns='<a href="(?P<Next>.*)"  class="pagnNext" id="pagnNextLink" title=".*">.*</a></span>'
compiledPagePatterns=compile(pagePatterns)							#对其进行预编译

#书籍具体信息2：作者，封面大图地址
detailPatterns_2='<div class="product-author">.*?<a href=".*">(?P<Author>.*)</a>&nbsp;.*?</div>[\s\S]*?'+\
			'<a href=.*? onClick=".*?"><img id="ImageShow" alt=".*" src="(?P<BigImgUrl>.*)" border="0" class="product-pic" /></a>'
compiledDetailPatterns_2=compile(detailPatterns_2)					#对其进行预编译

#原价#
opricePatterns='<li class="DetailPrice">[\s]*?'+\
					'.*?<strike><span class="PriceCharacter">.*?</span>(?P<OPrice>.*?)</strike>[\s]*?'+\
					'</li>'
compiledOpricePatterns=compile(opricePatterns)						#对其进行预编译

#卓越价#
pricePatterns='<li class="DetailOurPrice">[\s]*?'+\
					'.*?<span class="PriceCharacter">.*?</span><span class="OurPrice">(?P<Price>.*?)</span>'
compiledPricePatterns=compile(pricePatterns)							#对其进行预编译

#书籍基本信息：出版社，出版日期，版次，ISBN等#
infoPatterns='<span class="dark">(?P<InfoTitle>.*)</span>(?P<Info>.*)<br />'
compiledInfoPatterns=compile(infoPatterns)							#对其进行预编译

#内容简介#
captionPatterns='<hr>[\s]*?'+\
				'<h2 class="DetailTitle">内容简介</h2>[\s]*?'+\
				'<div class="ContentText">[\s]*?'+\
				'(?P<Caption>.*)[\s]*?'+\
				'</div>'
compiledCaptionPatterns=compile(captionPatterns)					#对其进行预编译