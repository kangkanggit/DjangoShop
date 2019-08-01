from django.urls import path,re_path
from Buyer.views import *
urlpatterns = [
    path('login/',login),#登录页面
    path('register/',register),#注册页面
    path('index/',index),#主页面
    path('logout/',logout),#退出功能
    path('user_site/',user_site),#收货地址页面
    path('user_infor/',user_infor),#个人信息也
    path('user_order/',user_order),#查看订单页
    path('show_goodlists/',show_goodlists),#商品的展示页
    path('car/',car),#购物车功能
    path('show_shop/',show_shop),#商品的详细页面
    path('pay_order/',pay_order),#提交订单页面
    path('pay_money/',pay_money),#支付功能
    re_path(r'^show_shop/(?P<goods_id>\d+)',show_shop),#商品的详细页面

]
urlpatterns +=[
    path('base/',base),#模板页面
    path('ajax_add/',ajax_add),#商品增加功能
    path('ajax_minus/',ajax_minus),#商品减少功能的验证
    path('ajax_show/',ajax_show),#商品详细页面输入功能的ajax的验证
    path('ajax_register/',ajax_register),#ajax的前端注册验证
    path('adds_car/',adds_car),#加入购物车功能
    path('list_add/',list_add),#列表表页加入购物车功能


]