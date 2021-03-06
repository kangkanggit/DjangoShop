from django.urls import path,include,re_path
from Store.views import *
urlpatterns = [
    path('register/',register),#注册页面
    re_path('^$',login),#登录页面
    path('login/',login),#登录页面
    path('index/',index),#主页面

    path('add_storeType/',add_storeType),#增加店铺类型
    path('regs/',register_store),#店铺注册页面

    path('good_Goods/',good_Goods),#增加商品功能
    re_path(r'^goods/(?P<goods_id>\d+)',goods),#商品的详情页
    re_path(r'update_goods/(?P<goods_id>\d+)',update_goods),#商品的修改页面
    path('delete_store/',delete_store),#商品的移除功能
    path('add_goodsType/',add_goodsType),#商品类型的页面
    path('dele_type/',dele_type),#删除商品

    re_path(r'goods_under/(?P<status>\w+)',set_goods),#商品的下上架功能
    re_path(r'list_goods/(?P<status>\w+)',list_goods),#店铺的商品展示页面

    path('order_list/',order_list),#订单列表页
    path('confirm/',confirm),#确认订单
    path('ok_order/',ok_order),#已处理订单页面
    path('show_order/',show_order),#订单详细
    path('delete_order/', delete_order),  # 删除订单


    path('login_out/',login_out),#退出登陆

]
from django.views.decorators.cache import cache_page

urlpatterns += [
    path('base/',base),  # 模板版页面
    path('ajx/',ajax_vaild),#ajax的前端验证注册验证
    path('ajax_type/', ajax_type),  # ajax的店铺类型前端验证
    path('swv/',cache_page(15*60)(small_white_views)),#声明缓存
    path('ajd/',ajax_goods_list),#vu测试
    path('get_add/',get_add),#celery的服务定时服务
    path('ajax_login/',ajax_login),#登录的ajax的验证

]