from django.urls import path,include,re_path
from Store.views import *

urlpatterns = [
    path('register/',register),#注册页面
    path('login/',login),#登录页面
    re_path('^$',index),#主页面
    path('index/',index),#主页面
    path('ajx/',ajax_vaild),#ajax的前端验证
    path('regs/',register_store),#店铺注册页面
    path('base/',base),  # 模板版页面
    path('good_Goods/',good_Goods),#增加商品功能
    path('list_goods/',list_goods),#店铺的商品管理页
    path('delete_store/',delete_store),#商品的移除功能
    re_path(r'^goods/(?P<goods_id>\d+)',goods),#商品的详情页
    re_path(r'update_goods/(?P<goods_id>\d+)',update_goods),#商品的修改页面

]
