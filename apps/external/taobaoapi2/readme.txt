TaoBao Open API2.0 for Python

http://code.google.com/p/python-taobao-open-sdk2/


大家好，我是duma 。
我是个python爱好者。
我要贡献出自己封装好的 taobao api ，目前只针对OPEN 2.0 版本。
下面我来简单介绍使用方法 ：

普通用法:

from taobaoapi2 imoprt *

itemsget = ItemsGet()
itemsget.setParams(nicks='etanliuyang')
itemsget.fetch()
for x in itemsget.datas:
  print x['title']

错误信息处理：

from taobaoapi2 imoprt *

itemsget = ItemsGet()
itemsget.setParams(nicks='v')
itemsget.fetch()
if itemsget.error_msg: print itemsget.error_msg