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
                    response.set_cookie('user.id',user.id)
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
    """
    判断是否有店铺
    检查当前用户是谁
    """
    user_id = request.COOKIES.get('user_id')
    if user_id:
        user_id = int(user_id)
    else:
        user_id = 0
    store = Store.objects.filter(user_id=user_id).first()
    if store:
        is_store = 1
    else:
        is_store = 0
    return render(request, 'store/index.html',{'is_store':is_store})



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

#店铺注册页面
def register_store(request):
    type_list = StoreType.objects.all()#查询类型
    if request.method == 'POST':
        post_data = request.POST#获取前端页面的信息
        store_name = post_data.get('store_name')
        store_address = post_data.get('store_address')
        store_description = post_data.get('store_description')
        store_phone = post_data.get('store_phone')
        store_money = post_data.get('store_money')

        user_id = int(request.COOKIES.get('user.id'))#验证的信息字段
        type_lists = post_data.getlist('type')#类型多对多的关系返回的是一个列表
        print(type_lists)
        store_logo = request.FILES.get('store_logo')#获取照片的字段

        #保存数据
        store = Store()
        store.store_name = store_name
        store.store_address = store_address
        store.store_description = store_description
        store.store_phone = store_phone
        store.store_money = store_money
        store.user_id = user_id
        store.store_logo = store_logo
        store.save()#保存数据
        for i in type_lists:#遍历列表内容依次保存
            store_type = StoreType.objects.get(id=i)
            print(store_type)
            store.type.add(store_type)
        store.save()#保存数据
    return render(request,'store/register_store.html',locals())



#增加商品的页面
def good_Goods(request):
    if request.method == "POST":
        goods_name = request.POST.get('goods_name')
        goods_price = request.POST.get('goods_price')
        goods_number = request.POST.get('goods_number')
        goods_description = request.POST.get('goods_description')
        goods_date = request.POST.get('goods_date')
        goods_safeDate = request.POST.get('goods_safeDate')
        goods_image = request.FILES.get('goods_image')
        good_store = request.POST.get('good_store')
        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number  = goods_number
        goods.goods_description = goods_description
        goods. goods_date =  goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        goods.save()#保存数据
        goods.store_id.add(
            Store.objects.get(id=int(good_store))
        )
        goods.save()#保存数据
    return render(request, 'store/add_Goods.html')


#商品的展示页面
def list_goods(request):
    keywords = request.GET.get('keyword','')
    if keywords:
        good_list = Goods.objects.filter(goods_name__contains=keywords)
    else:
        good_list = Goods.objects.all()
    return render(request,'store/list_goods.html',locals())


#模板页面
def base(request):
    return render(request, 'store/blank.html')


#退出功能
def login_out(request):
    response = HttpResponseRedirect('/Store/login/')
    response.delete_cookie('username')
    return response
# Create your views here.
