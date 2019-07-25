from django.urls import path,re_path
from Buyer.views import *
urlpatterns = [
    path('login/',login),#登录页面
    path('register/',register),#注册页面
    path('index/',index),#主页面

]
urlpatterns +=[
    path('base/',base),#模板页面

]