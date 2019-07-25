import hashlib

from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator#分页模块
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
    result = {'content':''}#返回的判断
    response = render(request,'store/login.html',locals())
    response.set_cookie('login_from','login_page')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:#检测用户密码是否不为空
            user = Seller.objects.filter(username=username).first()
            if user:#如果用户名正确
                cookies = request.COOKIES.get('login_from')
                if setPassword(password) == user.password and cookies == 'login_page':#判断是登陆页面过来的
                    response = HttpResponseRedirect('/Store/index/')
                    response.set_cookie('username',username)
                    response.set_cookie('user_id',user.id)
                    request.session['username'] = username
                    store = Store.objects.filter(user_id=user.id).first()
                    if store:
                        response.set_cookie('has_store',store.id)
                    else:
                        response.set_cookie('has_store','')
                    return response
                else:
                    result['content'] = '密码错误'
            else:
                result['content'] = '用户不存在'
    return response

@loginValid
#主页面
def index(request):
    return render(request, 'store/index.html')



#ajax注册验证
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
@loginValid
def register_store(request):
    type_list = StoreType.objects.all()#查询类型将他加载到前端页面
    if request.method == 'POST':
        post_data = request.POST#获取前端页面的信息
        store_name = post_data.get('store_name')
        store_address = post_data.get('store_address')
        store_description = post_data.get('store_description')
        store_phone = post_data.get('store_phone')
        store_money = post_data.get('store_money')

        user_id = int(request.COOKIES.get('user_id'))#验证的信息字段
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
            # print(store_type)
            store.type.add(store_type)
        store.save()#保存数据
        response = HttpResponseRedirect('/Store/index/')#跳转到主页面
        response.set_cookie('has_store',store.id)#并设置cookie
        return response
    return render(request,'store/register_store.html',locals())



#增加商品的页面
@loginValid
def good_Goods(request):
    if request.method == "POST":
        goods_name = request.POST.get('goods_name')
        goods_price = request.POST.get('goods_price')
        goods_number = request.POST.get('goods_number')
        goods_description = request.POST.get('goods_description')
        goods_date = request.POST.get('goods_date')
        goods_safeDate = request.POST.get('goods_safeDate')
        goods_image = request.FILES.get('goods_image')
        good_store = request.POST.get('good_store')#获取对应的id
        # print(good_store)
        goods = Goods()#获取类的实例
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number  = goods_number
        goods.goods_description = goods_description
        goods. goods_date =  goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        goods.save()#保存数据
        goods.store_id.add(
            Store.objects.get(id=int(good_store))#多对一的保存形式
        )
        goods.save()#保存数据
        return HttpResponseRedirect('/Store/list_goods/up/')
    return render(request, 'store/add_Goods.html')


#商品的展示页面
def list_goods(request,status):
    """
    写入展示页面的功能
    """
    if status == 'up':
        status_num = 1
    else:
        status_num = 0
    keywords = request.GET.get('keyword','')#实现模糊查找
    page_num = request.GET.get('page_num',1)#获取页面
    muns = request.POST.get('mun',2)#获取前端数据
    #查询店铺
    store_id = request.COOKIES.get('has_store')
    store = Store.objects.get(id=int(store_id))#查到对应的商品
    if keywords:
        good_list = store.goods_set.filter(goods_name__contains=keywords,goods_under=status_num)#从数据库中模糊查找
    else:
        good_list = store.goods_set.filter(goods_under=status_num)#展示所有
    paginator = Paginator(good_list,muns)#展示的内容和每一页展示的数据
    pages = paginator.count#获取数据的总条数
    list_sum = paginator.num_pages#总页数
    print(page_num)
    page = paginator.page(int(page_num))#获取展示页数对应的内容
    print(page)
    page_range = paginator.page_range#获取页面列表数
    next_page = int(page_num)#下一页默认等于当前页加一
    go_page = int(page_num)#上一页默认当前页减一
    #判断是下一页最后一页
    print(next_page)
    print(next_page)
    # 判断是否为第最后一页
    if next_page == list_sum:
        next_page = 0
    else:
        next_page += 1
    # 判断是否为第第一页
    if go_page == 1:
        go_page = 0
    else:
        go_page -= 1
    return render(request,'store/list_goods.html',{'page':page,'page_range':page_range,'keywords':keywords,
                                                   'pages':pages,'list_sum':list_sum,
                                                   'next_page':next_page,'go_page':go_page
                                                   ,'page_num':page_num,'status':status})



#商品的详情页
def goods(request,goods_id):
    goods_data = Goods.objects.filter(id=goods_id).first()
    return render(request,'store/goods.html',locals())


#商品的下架功能
def set_goods(request,status):
    if status == 'up':
        status_num = 1
    else:
        status_num = 0
    id = request.GET.get('id')
    referer = request.META.get('HTTP_REFERER')
    if id:
        goods = Goods.objects.filter(id=int(id)).first()
        print(goods)
        goods.goods_under = status_num
        goods.save()#保存数据
    return HttpResponseRedirect(referer)#返回当前页面

#移除功能
def delete_store(request):
    id = request.GET.get('id')
    Goods.objects.get(id=id).delete()
    return HttpResponseRedirect('/Store/list_goods/')

#商品修改功能
def update_goods(request,goods_id):
    goods_data = Goods.objects.filter(id=goods_id).first()
    if request.method == "POST":
        goods_name = request.POST.get('goods_name')
        goods_price = request.POST.get('goods_price')
        goods_number = request.POST.get('goods_number')
        goods_description = request.POST.get('goods_description')
        goods_date = request.POST.get('goods_date')
        goods_safeDate = request.POST.get('goods_safeDate')
        goods_image = request.FILES.get('goods_image')
        goods = Goods.objects.get(id=goods_id)#获取对应的值
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        if goods_image:
            goods.goods_image = goods_image
        goods.save()  # 保存数据
        return HttpResponseRedirect('/Store/goods/%s'%goods_id)#返回对应的商品页
    return render(request,'store/upadta_goods.html',locals())


#商品类型增加页面
def add_storeType(request):
    result = {'status':'error','content':''}
    if request.method == 'POST':
        store_type = request.POST.get('store_type')
        print(2)
        print(store_type)
        type_description = request.POST.get('type_description')
        print(type_description)
        if store_type and type_description:
            stype = StoreType()
            stype.store_type = store_type
            stype.type_description = type_description
            stype.save()#保存到数据库
            return HttpResponseRedirect('/Store/index/')
        else:
            result['content'] = '不能为空'
    return render(request,'store/add_sroteType.html')


#商品类型的ajax的前端验证
def ajax_type(request):
    restul = {'status':'error','content':''}
    if request.method == 'GET':
        id_store_type = request.GET.get('id_store_type')
        if id_store_type:
            types = StoreType.objects.filter(store_type=id_store_type).first()
            # print(types)
            if types:
                restul['content'] = '类型名存在'
            else:
                restul['content'] = '类型名可以用'
                restul['status'] = 'success'
        else:
            restul['content'] = '不可以不填'
    return JsonResponse(restul)



#模板页面
def base(request):
    return render(request, 'store/blank.html')


#退出功能
def login_out(request):
    response = HttpResponseRedirect('/Store/login/')
    for i in request.COOKIES:
        response.delete_cookie(i)
    return response
# Create your views here.
