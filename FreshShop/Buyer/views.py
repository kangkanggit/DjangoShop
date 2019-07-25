from django.shortcuts import render
from django.http import  HttpResponseRedirect

from Buyer.models import *
from Store.views import setPassword #


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
    return render(request,'buyer/index.html')


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
