"""FreshShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from Buyer.views import index
from rest_framework import routers
from Store.views import UserViewSet
from Store.views import TypeViewSet

router = routers.DefaultRouter()#默认路由
router.register(r"goodsType",TypeViewSet)#注册写好的接口
router.register(r"goods",UserViewSet)#注册写好的接口


urlpatterns = [
    path('admin/', admin.site.urls),
    path('Store/',include('Store.urls')),
    path('Buyer/',include('Buyer.urls')),
    re_path(r'^$',index),#主页路由
    path('ckeditor/',include('ckeditor_uploader.urls')),
    re_path('^API', include(router.urls)), #restful 的根路由
    re_path('^api-auth',include('rest_framework.urls')) #接口认真

]

