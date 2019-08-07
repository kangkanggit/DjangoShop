import hashlib

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.paginator import Paginator#分页模块
from django.shortcuts import HttpResponseRedirect
from django.views.decorators.cache import cache_page#缓存模块

from Store.models import *
from Buyer.models import *

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
    result = {'content': ''}  # 返回的判断
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
                    # return response
                else:
                    result['content'] = '密码错误'
            else:
                result['content'] = '用户不存在'
        else:
            result['content'] = '用户名密码不可以为空'
    return response


#登录功能的ajax的请求
def ajax_login(request):
    result = {'content':''}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username:
            user = Buyer.objects.filter(username=username).first()#查询名字是否在
            if user:
                psw = user.password
                if setPassword(password ) == psw :
                    pass
                else:
                    result['content'] = '密码错误或不可以为空'
            else:
                result['content'] = '用户名不存在'
        else:
            result['content'] = '用户密吗不可以为空'
    return JsonResponse(result)

#计算单个商品的剩余量
def const(count):
    orders = Order.objects.filter(order_status=3)#查询所有的详细订单发货的订单
    counts = sum([i.goods_count for i in orders])#获取销售的商品数量
    countds = count-counts#计算剩余的数据
    shengyu = str(((countds / count) * 100))[:5]#计算出剩余的百分比
    return shengyu
#计算商品中数的剩余量
def shop_count(shop):
    goods = Goods.objects.filter(goods_name=shop).first()#获取具体的商品

    order = OrderDetail.objects.filter(goods_name=goods.goods_name,order_id__order_status=3).all()#获取商品的订单

    if order :
        shops = sum([i.goods_number for i in order])#计算这个商品买出的个数
        goods_ck = goods.goods_number - shops

        if shops == goods.goods_number : #如果全部卖出的话
            goods.goods_number = 0
            goods.save()#修改数据情况库存
        return  goods_ck
    return goods.goods_number


@loginValid
#主页面
def index(request):
    keywords = request.GET.get('keyword', '')  # 实现模糊查找
    page_num = request.GET.get('page_num', 1)  # 获取页面
    muns = request.POST.get('mun', 5)  # 获取前端数据
    user_id = request.COOKIES.get('username')
    store_id = request.COOKIES.get('has_store')#获取店铺id
    goods_type = GoodsType.objects.all()
    store = Store.objects.filter(id=store_id).first()#获取对应的店铺
    money = store.store_money#得到店铺的起步资金
    goods_list = Goods.objects.filter(store_id=store_id)#获取商店对应的商品
    for i in goods_list:
        munds = shop_count(i.goods_name)#计算卖出的数量
        sheng_yu = str((( munds / i.goods_number) * 100))[:5]  # 计算出剩余的百分比
        i.goods_less = sheng_yu
        i.save()#保存数据
    if keywords:
        goods_list1 = Goods.objects.filter(store_id=store_id,goods_name=keywords,goods_under=1)#获取最新商品
    else:
        goods_list1 = Goods.objects.filter(store_id=store_id,goods_under=1) # 获取最新商品
    paginator = Paginator(goods_list1, muns)  # 展示的内容和每一页展示的数据
    pages = paginator.count  # 获取数据的总条数
    list_sum = paginator.num_pages  # 总页数
    page = paginator.page(int(page_num))  # 获取展示页数对应的内容
    if not page:
        if not page and int(page_num) == 1:
            return render(request, 'store/order_list.html')
        else:
            page = paginator.page(int(page_num) - 1)  # 获取展示页数对应的内容
    page_range = paginator.page_range  # 获取页面列表数
    next_page = int(page_num)  # 下一页默认等于当前页加一
    go_page = int(page_num)  # 上一页默认当前页减一
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
    mum = len(goods_list)#商品的数量
    count = sum([i.goods_number for i in goods_list])#获取库存状态
    counts = const(count)#计算剩余数量
    orderd_list = Order.objects.all()#查询所有的订单
    moneys = sum([i.order_price for i in orderd_list])#获取店铺的收入
    return render(request, 'store/index.html',locals())


#ajax注册验证
def ajax_vaild(request):
    restul = {'status':'error','content':''}
    if request.method == 'GET':
        username = request.GET.get('username')
        print(username)
        # print(type(a))
        if username:
            user = Seller.objects.filter(username=username)
            # print(user)
            if user:
                restul['content'] = '用户名存在'
            else:
                restul['content'] = '用户名可以用'
                restul['status'] = 'success'
        else:
            restul['content'] = '用户名密码不为空'
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
    goods_type = GoodsType.objects.all()
    if request.method == "POST":
        goods_name = request.POST.get('goods_name')
        goods_price = request.POST.get('goods_price')
        goods_number = request.POST.get('goods_number')
        goods_description = request.POST.get('goods_description')
        goods_date = request.POST.get('goods_date')
        goods_safeDate = request.POST.get('goods_safeDate')
        goods_image = request.FILES.get('goods_image')
        goods_introduce = request.POST.get('goods_introduce')
        good_store = request.POST.get('good_store')#获取对应的id
        goods_type = request.POST.get('type')
        goods = Goods()#获取类的实例
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number  = goods_number
        goods.goods_description = goods_description
        goods. goods_date =  goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        goods.goods_introduce = goods_introduce
        goods.goods_type = GoodsType.objects.get(id = goods_type)#多对一保存
        goods.store_id = Store.objects.get(id=int(good_store))
        goods.save()#保存数据
        return HttpResponseRedirect('/Store/list_goods/up/')
    return render(request, 'store/add_Goods.html',locals())


#商品的展示页面
def list_goods(request,status):
    """
    写入展示页面的功能
    《需要要优化页面显示功能》
    """
    if status == 'up':
        status_num = 1
    else:
        status_num = 0
    keywords = request.GET.get('keyword','')#实现模糊查找
    page_num = request.GET.get('page_num',1)#获取页面
    muns = request.POST.get('mun',6)#获取前端数据
    #查询店铺
    store_id = request.COOKIES.get('has_store')
    store = Store.objects.get(id=int(store_id))#查到对应的商点
    if keywords:
        good_list = store.goods_set.filter(goods_name__contains=keywords,goods_under=status_num).order_by('-id')#从数据库中模糊查找
    else:
        good_list = store.goods_set.filter(goods_under=status_num).order_by('-id')#展示所有
    paginator = Paginator(good_list,muns)#展示的内容和每一页展示的数据
    pages = paginator.count#获取数据的总条数
    list_sum = paginator.num_pages#总页数
    page = paginator.page(int(page_num))  # 获取展示页数对应的内容
    if not page:
        if not page and int(page_num) == 1:
            return render(request, 'store/order_list.html')
        else:
            page = paginator.page(int(page_num) - 1)  # 获取展示页数对应的内容
    page_range = paginator.page_range#获取页面列表数
    next_page = int(page_num)#下一页默认等于当前页加一
    go_page = int(page_num)#上一页默认当前页减一
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

        goods.goods_under = status_num
        goods.save()#保存数据
    return HttpResponseRedirect(referer)#返回当前页面

#移除功能
def delete_store(request):
    referer = request.META.get('HTTP_REFERER')
    id = request.GET.get('id')
    Goods.objects.get(id=id).delete()
    return HttpResponseRedirect(referer)

#商品修改功能
def update_goods(request,goods_id):
    goods_data = Goods.objects.filter(id=goods_id).first()
    goods_type = GoodsType.objects.all()
    if request.method == "POST":
        goods_name = request.POST.get('goods_name')
        goods_price = request.POST.get('goods_price')
        goods_number = request.POST.get('goods_number')
        goods_description = request.POST.get('goods_description')
        goods_date = request.POST.get('goods_date')
        goods_introduce = request.POST.get('goods_introduce')
        goods_safeDate = request.POST.get('goods_safeDate')
        goods_image = request.FILES.get('goods_image')
        goods_type = request.POST.get('type')
        # print(goods_type)
        goods = Goods.objects.get(id=goods_id)#获取对应的值
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_introduce = goods_introduce
        goods.goods_safeDate = goods_safeDate
        goods.goods_type = GoodsType.objects.get(id = goods_type)
        if goods_image:
            goods.goods_image = goods_image
        goods.save()  # 保存数据
        return HttpResponseRedirect('/Store/goods/%s'%goods_id)#返回对应的商品页
    return render(request,'store/upadta_goods.html',locals())


#商店类型增加页面
def add_storeType(request):
    result = {'status':'error','content':''}
    if request.method == 'POST':
        store_type = request.POST.get('store_type')
        type_description = request.POST.get('type_description')
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


#增加和展示商品类型
def add_goodsType(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        picture = request.FILES.get('picture')
        if name and description and picture:
            goods_type = GoodsType()
            goods_type.name = name
            goods_type.description = description
            goods_type.picture = picture
            goods_type.save()#保存到数据库中
            return HttpResponseRedirect('/Store/add_goodsType/')
    keywords = request.GET.get('keyword', '')  # 实现模糊查找
    page_num = request.GET.get('page_num', 1)  # 获取页面
     # 查到对应的类型
    if keywords:
        good_list = GoodsType.objects.filter(goods_name__contains=keywords).order_by('-id')  # 从数据库中模糊查找
    else:
        good_list = GoodsType.objects.all().order_by('-id')  # 展示所有
    paginator = Paginator(good_list, 3)  # 展示的内容和每一页展示的数据
    pages = paginator.count  # 获取数据的总条数
    list_sum = paginator.num_pages  # 总页数
    page = paginator.page(int(page_num))  # 获取展示页数对应的内容
    if not page:
        if not page and int(page_num) == 1:
            return render(request, 'store/order_list.html')
        else:
            page = paginator.page(int(page_num) - 1)  # 获取展示页数对应的内容

    page_range = paginator.page_range  # 获取页面列表数
    next_page = int(page_num)  # 下一页默认等于当前页加一
    go_page = int(page_num)  # 上一页默认当前页减一
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
    return render(request, 'store/show_goodsType.html',locals())

#删除商品类型
def dele_type(request):
    id = request.GET.get('id')
    GoodsType.objects.get(id=id).delete()
    return HttpResponseRedirect('/Store/add_goodsType/')


#订单展示页面
def order_list(request):
    list_order3 = []
    store_id = request.COOKIES.get('has_store')#获取店铺id
    page_num = request.GET.get('page_num', 1)  # 获取页面
    keywords = request.GET.get('keyword', '')  # 实现模糊查找
    if keywords:
        list_order1 = OrderDetail.objects.filter(order_id__order_status=2,goods_store=store_id,goods_name__contains=keywords).order_by('-id')#查询订单付款的订单
        for i in list_order1 :#循环查询的对象
            if i.order_id not in list_order3:
                list_order3.append(i.order_id)
    else:
        list_order1 = OrderDetail.objects.filter(order_id__order_status=2, goods_store=store_id).order_by('-id')  # 查询订单付款的订单对应店铺的id
        for i in list_order1 :#循环查询的对象
            if i.order_id not in list_order3:
                list_order3.append(i.order_id)

    paginator = Paginator(list_order3, 6)  # 展示的内容和每一页展示的数据
    pages = paginator.count  # 获取数据的总条数
    list_sum = paginator.num_pages  # 总页数
    page = paginator.page(int(page_num))  # 获取展示页数对应的内容
    if not page:
        if not page and int(page_num) == 1:
            return render(request, 'store/order_list.html')
        else:
            page = paginator.page(int(page_num) - 1)  # 获取展示页数对应的内容
    page_range = paginator.page_range  # 获取页面列表数
    next_page = int(page_num)  # 下一页默认等于当前页加一
    go_page = int(page_num)  # 上一页默认当前页减一
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
    return render(request,'store/order_list.html',locals())

#确认订单功能
def confirm(request):
    order_id = request.GET.get('order_id')#获取详细订单表的id
    # print(order_id)
    order = Order.objects.get(id=order_id)#获取对应的订单
    order.order_status = 3
    order.save()#保存数据
    return HttpResponseRedirect('/Store/order_list')

#订单详细页面
def show_order(request):
    order_id = request.GET.get('order_id')#获取订单的id
    order = Order.objects.get(id=order_id)#得到id
    order_list1 = order.orderdetail_set.all()#查询详细的订单
    return render(request,'store/show_order.html',locals())


#删除订单
def delete_order(request):
   order_id = request.GET.get('order_id')#获取订单的id
   #订单和订单详细是外键关系所以删除主键外键也会删除
   order = Order.objects.get(id=order_id)#查询对应的订单
   order.delete()#最后删除这个订单
   return HttpResponseRedirect('/Store/order_list')
#已处理订单列表
def ok_order(request):
    list_order3 = []
    store_id = request.COOKIES.get('has_store')  # 获取店铺id
    page_num = request.GET.get('page_num', 1)  # 获取页面
    keywords = request.GET.get('keyword', '')  # 实现模糊查找
    if keywords:
        list_order1 = OrderDetail.objects.filter(order_id__order_status=3, goods_store=store_id,
                                                 goods_name__contains=keywords).order_by('-id')  # 查询订单付款的订单
        for i in list_order1:  # 循环查询的对象
            if i.order_id not in list_order3:
                list_order3.append(i.order_id)
    else:
        list_order1 = OrderDetail.objects.filter(order_id__order_status=3, goods_store=store_id).order_by('-id') # 查询订单付款的订单对应店铺的id
        for i in list_order1:  # 循环查询的对象
            if i.order_id not in list_order3:
                list_order3.append(i.order_id)
    paginator = Paginator(list_order3, 6)  # 展示的内容和每一页展示的数据
    pages = paginator.count  # 获取数据的总条数
    list_sum = paginator.num_pages  # 总页数
    page = paginator.page(int(page_num))  # 获取展示页数对应的内容
    if not page:
        if not page and int(page_num) == 1:
            return render(request, 'store/order_list.html')
        else:
            page = paginator.page(int(page_num) - 1)  # 获取展示页数对应的内容
    page_range = paginator.page_range  # 获取页面列表数
    next_page = int(page_num)  # 下一页默认等于当前页加一
    go_page = int(page_num)  # 上一页默认当前页减一
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
    return render(request,'store/ok_order.html',locals())


#模板页面
def base(request):
    return render(request, 'store/blank.html')


#退出功能
def login_out(request):
    response = HttpResponseRedirect('/Store/login/')
    for i in request.COOKIES:
        response.delete_cookie(i)
    return response

def ajax_goods_list(request):
    return render(request,'store/ajax_goods_list.html')


from rest_framework import viewsets
from Store.serializers import *
from django_filters.rest_framework import DjangoFilterBackend#导入过滤器

class UserViewSet(viewsets.ModelViewSet):
    #返回具体查询的内容
    queryset = Goods.objects.all()#具体数据
    serializer_class = UserSerializer#指定过滤的类

    filter_backends = [DjangoFilterBackend]#采用那个过滤器
    filterset_fields = {'goods_name','goods_price'}#进行查询的字段



class TypeViewSet(viewsets.ModelViewSet):
    queryset = GoodsType.objects.all()
    serializer_class = GoodsTypeSerializer



from django.core.mail import  send_mail
def sendMail(request):
    send_mail('邮件主题','邮件内容','from_email',['to_email'],fail_silently=False)


#调用celery服务
from CeleryTask.tasks import add
from django.http import JsonResponse

def get_add(request):
    add.delay(2,3)
    return JsonResponse({"statue":200})


#案例中间件视图

@cache_page(60*50)
def small_white_views(request):
    # print('我是哈哈')
    # return JsonResponse({'name':'小李','age':15})
    return HttpResponse('我是缓存，测试')

# Create your views here.
