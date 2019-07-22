from django.urls import path,include,re_path
from Store.views import *

urlpatterns = [
    path('register/',register),#注册页面
    path('login/',login),#登录页面
    re_path('^$',index),#主页面
    path('index/',index),#主页面
]