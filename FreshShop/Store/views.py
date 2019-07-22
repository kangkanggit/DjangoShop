import hashlib

from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import HttpResponseRedirect

from Store.models import *

#加密
def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result

#登录验证装饰器
def loginValid(fun):
    def inner(request,*args,**kwargs):
        k_user = request.COOKIES.get('username')
        s_user = request.session.get('username')
        if k_user and s_user:
            user = Seller.objects.filter(username=k_user).first()
            if user and k_user == s_user:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect('/Store/login/')
    return inner
#注册功能
def register(request):
    """
    register注册
    完成注册
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            seller = Seller()
            seller.username = username
            seller.password = setPassword(password)
            seller.nickname = username
            seller.save()#保存数据
            return HttpResponseRedirect('/Store/login/')
    return render(request,'store/register.html',locals())

#登录功能
def login(request):
    """
    登录功能，登录成功，跳转到首页
    失败跳转到，登录页面
    """
    result = {'content':''}
    response = render(request,'store/login.html',locals())
    response.set_cookie('login_from','login_page')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = Seller.objects.filter(username=username).first()
            if user:
                cookies = request.COOKIES.get('login_from')
                if setPassword(password) == user.password and cookies:
                    response = HttpResponseRedirect('/Store/index/')
                    response.set_cookie('username',username)
                    request.session['username'] = username
                    return response
                else:
                    result['content'] = '密码错误'
            else:
                result['content'] = '用户不存在'
    return response

@loginValid
#主页面
def index(request):
    return render(request,'store/index.html',locals())



#ajax验证
def ajax_vaild(request):
    restul = {'status':'error','content':''}
    if request.method == 'GET':
        username = request.GET.get('username')
        if username:
            user = Seller.objects.filter(username=username).first()
            if user:
                restul['content'] = '用户名存在'
            else:
                restul['content'] = '用户名可以用'
                restul['status'] = 'success'
        else:
            restul['content'] = '用户名不为空'
    return JsonResponse(restul)

#模板页面
def base(request):
    return render(request,'store/blank.html')


#退出功能
def login_out(request):
    response = HttpResponseRedirect('/Store/login/')
    response.delete_cookie('username')
    return response
# Create your views here.
