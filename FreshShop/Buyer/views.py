from django.shortcuts import render
from django.http import  HttpResponseRedirect

from Buyer.models import *
from Store.views import setPassword #
from Store.models import *


#登录验证装饰器
def loginValid(fun):
    def inner(request,*args,**kwargs):
        k_user = request.COOKIES.get('username')
        s_user = request.session.get('username')
        if k_user and s_user:
            user = Buyer.objects.filter(username=k_user).first()
            if user and k_user == s_user:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect('/Buyer/login/')
    return inner

#登录页面
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        if username and password:
            user = Buyer.objects.filter(username=username).first()
            if user:
                web_password = setPassword(password)
                if web_password == user.password:
                    response = HttpResponseRedirect('/Buyer/index/')
                    response.set_cookie('username',user.username)
                    response.set_cookie('user_id',user.id)
                    request.session['username'] = user.username
                    return response
    return render(request,'buyer/login.html')

#首页
@loginValid
def index(request):
    result_list = []
    goods_list_type = GoodsType.objects.all()#查询所有的类型
    for goods_type in goods_list_type:#遍历每一个类型
        goods_list = goods_type.goods_set.values()[:4]#查询4条语句
        if goods_list:#判断是否有类型
            goodsType = {
                'id':goods_type.id,#id的名字
                'name':goods_type.name,#类型名
                'description':goods_type.description,#类型描述
                'picture':goods_type.picture,#类型图片
                'goods_list':goods_list,#查询图片
            }
            result_list.append(goodsType)
    return render(request,'buyer/index.html',locals())


#注册功能
def register(request):
    if request.method == 'POST':
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        if username and password and email:
            buyer = Buyer()
            buyer.username = username
            buyer.password = setPassword(password)
            buyer.email = email
            buyer.save()#保存数据
            return HttpResponseRedirect('/Buyer/login/')
    return render(request,'buyer/register.html')

#ajax注册验证
def ajax_register(request):
   result = {'status':'error','content':''}
   username = request.GET.get('user_name')
   print(username)
   if username:
       buyer = Buyer.objects.filter(username=username).first()
       print(buyer)
       if buyer:
           result['content'] = '用户名存重复用'
       else:
           result['status'] = 'success'
           result['content'] = '用户名可以用'
   else:
       result['content'] = '用户名不可以为空'
   return result


#商品的更多页面
def show_goodlists(request):
    goodslist = []
    type_id = request.GET.get('type_id')
    goods_type = GoodsType.objects.filter(id=type_id).first()#查找对应的类型
    if goods_type:#如果存在
        goods_list = goods_type.goods_set.filter(goods_under=1)#返回在线的商品
    return render(request,'buyer/good_list.html',locals())

#退出功能
def logout(request):
    response = HttpResponseRedirect('/Buyer/login/')
    for key  in request.COOKIES:
        response.delete_cookie(key)
    del request.session['username']
    return response

#模板页面
def base(request):
    return render(request,'buyer/base.html')


# Create your views here.
