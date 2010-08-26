#coding=utf8

from base import TaoBao

class ShopGet(TaoBao):
    data_name = False
    data_type = 'shop'
    method = 'shop.get'
    fields = 'sid,cid,nick,title,desc,bulletin,pic_path,created,modified'