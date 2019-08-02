import time
from django.shortcuts import render
from django.http import JsonResponse
from django.http import  HttpResponseRedirect
from django.http import  HttpResponse

from Buyer.models import *
from Store.views import setPassword #
from Store.models import *
from alipay import AliPay


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
    count = 1
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
                'aid':goods_type.aid,#样式类型
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
   if request.method == 'GET':
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
   return JsonResponse(result)


#商品的更多页面
def show_goodlists(request):
    goodslist = []
    type_id = request.GET.get('type_id')
    goods_type = GoodsType.objects.filter(id=type_id).first()#查找对应的类型
    if goods_type:#如果存在goods_under商品的状态
        goods_list = goods_type.goods_set.filter(goods_under=1)#返回在线的商品
        goods_first = goods_type.goods_set.filter(goods_under=1).order_by('-id').first()#返回第一个商品
    return render(request,'buyer/good_list.html',locals())



#商品加入购物车的功能
def adds_car(request):
    result = {'state':'error','data':''}
    if request.method == 'POST':
        count = int(request.POST.get('count'))
        goods_id = request.POST.get('goods_id')#获取商品的id
        goods = Goods.objects.get(id=int(goods_id))
        user_id = request.COOKIES.get('user_id')

        cart = Cart()
        cart.goods_name = goods.goods_name#商品名字
        cart.goods_price = goods.goods_price#商品单价
        cart.goods_total = goods.goods_price*count#商品的总价
        cart.goods_number = count#商品的数量
        cart.goods_picture = goods.goods_image#商品的图片
        cart.goods_id = goods_id#商品id
        cart.goods_store = goods.store_id.id#商店id
        cart.user_id = user_id#用户id
        cart.goods_live = 0#购物车的状态
        cart.save()#保存数据
        result['status'] = 'success'
        result['data'] = '商品添加成功'
    else:
        result['data'] = '请求错误'
    return JsonResponse(result)

#列表页面的购物车功能
def list_add(request):
    if request.method == 'GET':
        count = int(request.GET.get('count'))
        goods_id = request.GET.get('goods_id')#获取商品的id
        goods = Goods.objects.get(id=int(goods_id))#获取对应的商品
        a= goods.goods_type.id
        print(a)
        user_id = request.COOKIES.get('user_id')#获取用户id

        cart = Cart()
        cart.goods_name = goods.goods_name#商品名字
        cart.goods_price = goods.goods_price#商品单价
        cart.goods_total = goods.goods_price*count#商品的总价
        cart.goods_number = count#商品的数量
        cart.goods_picture = goods.goods_image#商品的图片
        cart.goods_id = goods_id#商品id
        cart.goods_store = goods.store_id.id#商店id
        cart.user_id = user_id#用户id
        cart.save()#保存数据
        url = '/Buyer/show_goodlists/?type_id=%s'%a#获取当前的路由
        return HttpResponseRedirect(url)

#购物车功能
def car(request):
    user_id = request.COOKIES.get('user_id')#获取用户id
    goods_list = Cart.objects.filter(user_id=user_id,goods_live=0)#获取购物车列表
    h = [i.goods_total for i in goods_list]#循环购物车列表类
    money = sum(h)#计算总价钱
    number = len(goods_list)#统计商品个数

    if request.method == "POST":
        post_data = request.POST
        # print(post_data)
        cart_data = [] #收集商品
        for k,v in post_data.items():
            if k.startswith('goods_'):
                # print(k)
                # print(v)
                cart_data.append(Cart.objects.get(id=int(v)))
        # print(cart_data)
        goods_count = len(cart_data)#获取数据的数据
        goods_total = sum([int(i.goods_total) for i in cart_data])#订单和
        #保存订单
        order = Order()
        order.order_id = setOrder_id(str(user_id),str(goods_count),'3')
        # 订单当中有多个商品或者多个店铺，使用goods_count来代替商品id，
        order.goods_count = goods_count#商品总数
        order.order_user = Buyer.objects.get(id=user_id)#用户id
        order.order_price = goods_total#商品总价
        order.order_status =1
        order.save()

        #详细订单的保存
        # print(cart_data)
        for detail in cart_data:
            order_detail = OrderDetail()
            order_detail.order_id = order#订单号
            order_detail.goods_id = detail.goods_id#商品id
            order_detail.goods_name = detail.goods_name#商品名
            order_detail.goods_price = detail.goods_price#商品的单价
            order_detail.goods_number = detail.goods_number#商品的数量
            order_detail.goods_total = detail.goods_total#商品的总价
            order_detail.goods_store = detail.goods_store#店铺id
            order_detail.goods_image = detail.goods_picture#店铺图片
            order_detail.save()
        url = '/Buyer/pay_order/?order_id=%s'%order.id
        return HttpResponseRedirect(url)
    return render(request,'buyer/car.html',locals())


#商品的详情页
def show_shop(request,goods_id):
    goods = Goods.objects.filter(id=goods_id).first()#查询对应的商品
    goods_type = goods.goods_type#查询对应的商品类型
    return render(request,'buyer/show_shop.html',locals())

#订单生产
def setOrder_id(user_id,goods_id,store_id):
    #时间+用户id+商品id+商铺id
    strtime = time.strftime("%Y%m%d%H%M%S",time.localtime())
    return strtime+user_id+goods_id+store_id


#商品的提交订单页面
def pay_order(request):
    if request.method == "POST":
        detail = []
        # post数据
        count =int(request.POST.get("count"))#获取数量
        goods_id = request.POST.get("goods_id")#获取商品的id
        # cookie的数据
        user_id = request.COOKIES.get("user_id")
        buyer = Buyer.objects.filter(id=user_id).first()  # 查找对应的用户
        adds_list = buyer.address_set.all()  # 查找用户对应的地址
        # 数据库的数据
        goods = Goods.objects.get(id=goods_id)#查询对应的商品
        store_id = goods.store_id.id  # 获取商品对应的商店的id

        price = goods.goods_price#商品的单价

        #保存数据订单表
        order = Order()#保存订单表
        order.order_id = setOrder_id(str(user_id),str(goods_id),str(store_id))#生成订单表
        print(order.order_id)
        order.goods_count = count#保存商品的数量
        order.order_user = Buyer.objects.get(id=user_id)#订单用户
        order.order_price = count * goods.goods_price#订单的总价格
        order.order_status = 1
        order.save()#保存数据

        #保存订单详情表
        order_detail = OrderDetail()#保存订单的详情表
        order_detail.order_id = order
        order_detail.goods_id = goods_id#保存商品id
        order_detail.goods_name = goods.goods_name#保存商品的名
        order_detail.goods_price = goods.goods_price#保存商品的价格
        order_detail.goods_number = count#保存商品的数量
        order_detail.goods_total = count * goods.goods_price#保存商品的总价
        order_detail.goods_store = store_id#对应的商店id
        order_detail.goods_image = goods.goods_image#保存商品的图片
        order_detail.save()#保存数据

        detail = [order_detail]
        return render(request, "buyer/play_order.html",locals())
    else:
        order_id = request.GET.get('order_id')#获取订单id
        if order_id:
            order = Order.objects.get(id=order_id)
            detail = order.orderdetail_set.all()
            user_id = request.COOKIES.get("user_id")
            buyer = Buyer.objects.filter(id=user_id).first()  # 查找对应的用户
            adds_list = buyer.address_set.all()
            return render(request,'buyer/play_order.html',locals())
        else:
            return HttpResponse("非法请求，程序员在加班写这个功能中")


#支付功能
def pay_money(request):
    if request.method == "GET":
        order_id = request.GET.get('order')#得到订单号
        money = request.GET.get('money')#的钱数
        order = Order.objects.get(order_id=order_id)#的到订单号
        name = order.order_user.username#得到用户名
        alipay_public_key_string = """-----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAw33Gh5+47xMbHRi2FbdBoxJpje8cWtherlkmLbqCn4n8Wgz5dcoCi6YS/hPHHTeqKf6gNw4BnlYEDizpP/SWjD0NyBszn1wuzMX9jF4YwJ/bWOtPaGa91Bu26AGVoyILPtvMIMCMHlrvEOWJ9qcn8Nhf9i3W2nC+eO9OSHE61M1EtosQsqByLck8YmmeuRpPAtU8avUgfuTIQtri3ik3aSjaiqLFpfrBaPL19S9Ax6nfC/ZiI3eof7G0Nph2lt73IrNqOpU226ZetLJyDYp0Ou8kt185tiSeEOKf/ydx83fcSGj99SwnK4xb18/aysJ/LoyMbaGdQ00g/3kQ5GprpQIDAQAB
        -----END PUBLIC KEY-----"""

        app_private_key_string = """-----BEGIN RSA PRIVATE KEY-----
        MIIEowIBAAKCAQEAw33Gh5+47xMbHRi2FbdBoxJpje8cWtherlkmLbqCn4n8Wgz5dcoCi6YS/hPHHTeqKf6gNw4BnlYEDizpP/SWjD0NyBszn1wuzMX9jF4YwJ/bWOtPaGa91Bu26AGVoyILPtvMIMCMHlrvEOWJ9qcn8Nhf9i3W2nC+eO9OSHE61M1EtosQsqByLck8YmmeuRpPAtU8avUgfuTIQtri3ik3aSjaiqLFpfrBaPL19S9Ax6nfC/ZiI3eof7G0Nph2lt73IrNqOpU226ZetLJyDYp0Ou8kt185tiSeEOKf/ydx83fcSGj99SwnK4xb18/aysJ/LoyMbaGdQ00g/3kQ5GprpQIDAQABAoIBAC9BXhY2s9uGwM0dxhYlwEYNE1rt6+rB1tFKV4JCTYUHM+sIq9yfQlJDiN/GJCGZ7RZNqKjmR9ngbQaIMLH3C9VGhOhUOvxQqjdxvMKLlGwruDgcWYuhGk4FjQc0KtnORu2g8A0SvkwwKw3ojpsC+RKtGzVFC2SuUDynjELSrCf4MewCkNji47HfSQl4prlqsl05q+azrbPuMS5/BNO0ULCDtOedOD1azMDKW3O5JulC2WJM0HqJiGWGXZTeqI9O1NbZZwQDMeJPJGZHcEaivgvoI3S4/0iqK+yhMaGLeFZXsRChzwKTu2Qjf5tFvFg4uyEwjfBCvv2xqO6iICw5tYECgYEA9zpSQsY6YbeSQTQiqs1w+jNLdqwJlk6rXI2U3fPKJ3/53fu6uSnNiJu0pmpI2JtMxMRW8afEGnLbq/WoSEgsgm8rp7K+I+2smRPXO/jPyy14KPHpBG5CZk0J6llHBo+7sv77jZRz6rqFn1CI5Im4Efen4RnHW60LaR/c/5/Mf3UCgYEAym2CQIDxF4cBQIaDc3uvWKAoYGtRNZVJuVPcP+LjHKGXGI6+Kl75xJ76DHqiPE89a2Hc3ZIhdQzjbUNsQ2mQa+IhcIvganU2+Rb8Q8h4yGyLc6lWNknEWG0+1XhrCcntfWiJZpx3PigRTxVUm1dKjuyxje+vOBw9zCpIN/LJZXECgYBRP6d9LmxNZOj56Mpj27R/ZZAtZgiYjy4d8qGz98S+Cn7xhyMsayKS/Kj38AIUvaUTHXt9W6dFEe5Dqy4s4xtNmn98U2/NmvSYMj8QBIs1uLG+sxHjVOEZgcP6cnC3JVGIV+gP9XPK9pWnb+4tPV1y+jL/9VrhNBOF7uTQVZH9aQKBgH8kdxoioss/PZcUpb3EIudMeO/OmAxKvyqLNJxf2nwiNm/zQBgG3WQU4kMyR3IP5yjqJ7p3TVJijPoUzgwtYsuQFabGBGd5RdUADeRZJxvjqVc1NfQVMyDDRSL5ZmmYjfUl0p9DiVXd/rkoUaLcGfVZT1AyCmD4xAvXRtL1SG/RAoGBAJGhRj7R+E975ckb1bdDlR1mRWTvH14VTdamzi/L9jGY2x2aUISMAiZ/PdJTXtDHtqqLpOBSUoCIe60lQw07K6+G5LpY3ltTqiuUt6yyxZztvJCHEB4bSat8xYyN4G8eC5OnXrg658L+OR8Bp8obtLwNf3t9VQBOUqLldc2TcP3e
        -----END RSA PRIVATE KEY-----"""

        # 实例化支付应用
        alipay = AliPay(
            appid='2016101000652521',
            app_notify_url=None,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type='RSA2'
        )

        # 发起支付请请求
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单号
            total_amount=str(money),  # 支付金额
            subject=name,  # 交易主题
            return_url="http://10.10.21.75:8000/Buyer/user_order/",
            notify_url="http://10.10.21.75:8000/Buyer/user_order/",
        )
        order = Order.objects.get(order_id=order_id)#获取对应的订单实例
        order.order_status = 2
        order.save()#保存数据
        orders_list = order.orderdetail_set.all()#查询所有的详细订单
        for i in orders_list:

            a = i.goods_id#获取对应的商品名称

            card = Cart.objects.filter(goods_id=a,goods_live=0)
            for i in card:
                i.goods_live = 1
                i.save()
        return HttpResponseRedirect("https://openapi.alipaydev.com/gateway.do?" + order_string)


#用户中心的编写
#个人信息页面
@loginValid
def user_infor(request):
    result = {'name':'','phone':'','address':''}
    username = request.COOKIES.get('username')
    user_id = request.COOKIES.get('user_id')
    user = Buyer.objects.filter(id=user_id).first()
    phone = user.phone
    connect_address = user.connect_address
    if user:
        result['name'] = username
        result['phone'] = phone
        result['address'] = connect_address
    return render(request,'buyer/user_infor.html',{'result':result})


#获取订单时间的函数
def times(order):
    a = order.order_id
    c = a[:14]
    order_time = c[:4] + '-' + c[4:6] + '-' + c[6:8] + ' ' + c[8:10] + ':' + c[10:12] + ':' + c[12:]  # 生成订单时间
    return order_time

#编写订单页面(需要开发)
@loginValid
def user_order(request):
    list1 =[]
    k_user = request.COOKIES.get('username')
    s_user = request.session.get('username')
    if k_user == s_user:#为了保持是当前的用户
        user = request.COOKIES.get('user_id')#获取用户的id
        #未支付订单
        order_id2 = Order.objects.filter(order_status=1, order_user=user)  # 查询等于1的订单表总的
        if order_id2:
            for i in order_id2 :#获取总订单单个对象
                result2 = times(i)#获取时间
                # print(h)
        #发货订单
        order_id = Order.objects.filter(order_status=3,order_user=user)#查询等于3的订单表
        if order_id:
            for i in order_id:  # 获取总订单单个对象
                result = times(i)  # 获取时间
        #没发货订单
        order_id1 = Order.objects.filter(order_status=2,order_user=user)#查询等于2的订单表
        if order_id1:
            for i in order_id1:  # 获取总订单单个对象
                result1 = times(i)  # 获取时间

        #查询支付成功的订单表，并且店家确认的商品
        return render(request,'buyer/user_order.html',locals())
    return render(request,'buyer/index.html')

#详细订单
def show_order(request):
    order_id = request.GET.get('order_id')#获取订单的id
    order = Order.objects.get(id=order_id)#查询对应的订单
    order_list = order.orderdetail_set.all()
    return render(request,'buyer/user_show_order.html',locals())


#收货地址页面
@loginValid
def user_site(request):
    if request.method == "POST":
        #获取前端页面的数据
        recver = request.POST.get('recver')
        address = request.POST.get('address')
        post_number = request.POST.get('post_number')
        recver_phone = request.POST.get('recver_phone')
        buyer_id = request.POST.get('buyer_id')
        add = Address()#保存数据
        add.recver = recver
        add.address = address
        add.post_number = post_number
        add.recver_phone = recver_phone
        add.buyer_id = Buyer.objects.get(id=buyer_id)#多对一的保存
        add.save()#保存数据
        return HttpResponseRedirect('/Buyer/user_site/')#返回当前页
    else:
        user_id = request.COOKIES.get('user_id')
        # print(user_id)
        buyer = Buyer.objects.filter(id=user_id).first()#查找对应的用户
        # print(buyer)
        a = buyer.username
        # print(a)
        adds_list = buyer.address_set.all()  #查找用户对应的地址
    return render(request,'buyer/user_site.html',{'adds_list':adds_list})

#详细页面的前端输入ajax验证
def ajax_show(request):
    result = {'status':'error','money':''}
    if request.method == 'GET':
        mun = request.GET.get('mun')#获取框框的数据
        mund = int(mun)
        goods_id = request.GET.get('goods_id')#获取对应的id
        goods_mun = Goods.objects.filter(id=int(goods_id)).first()
        if  mund and  mund > 0:
           if  mund <= goods_mun.goods_number:
               result['money'] = (goods_mun.goods_price)*mund
               result['status']='success'
           else:
               result['status']='error'
        else:
            result['status']='error'
    return JsonResponse(result)

#详细页面的数量加减商品的数量
def ajax_add(request):
    result = {'status': 'error','number':'','money':''}
    if request.method == 'GET':
        muns = request.GET.get('muns')#获取前端的数据
        munsd = int(muns)
        goods_id = request.GET.get('goods_id')#获取对应的id
        goods_mun = Goods.objects.filter(id=int(goods_id)).first()#获取对应的商品
        if  goods_id  and munsd >= 0:#判断条件
            goods_number = goods_mun.goods_number#获取商品的库存
            if munsd < goods_number:
                result['status'] = 'success'
                result['number'] = munsd+1
                result['money'] = (goods_mun.goods_price) * (munsd+1)
            else:
                result['number'] = goods_number
                result['status'] = 'error'
        else:
            result['status'] = 'error'
    return JsonResponse(result)

#详细页面数量减少的功能
def ajax_minus(request):
    result = {'status': 'error', 'number': '','money':''}
    if request.method == 'GET':
        muns = request.GET.get('muns')  # 获取前端的数据
        munsd = int(muns)
        goods_id = request.GET.get('goods_id')  # 获取对应的id
        goods_mun = Goods.objects.filter(id=int(goods_id)).first()  # 获取对应的商品
        if muns and  munsd > 0:  # 判断条件
            if munsd > 1 :
                result['status'] = 'success'
                result['money'] = (goods_mun.goods_price) * (munsd-1)
                result['number'] = munsd - 1
            else:
                result['number'] = 1
                result['status'] = 'error'
        else:
            result['status'] = 'error'
    return JsonResponse(result)

#退出功能
def logout(request):
    response = HttpResponseRedirect('/Buyer/login/')
    for key  in request.COOKIES:
        response.delete_cookie(key)
    del request.session['username']
    return response

#购物车的删除功能
def delete_cart(request):
    return HttpResponseRedirect('Buyer/')


#模板页面
def base(request):
    return render(request,'buyer/base.html')

# Create your views here.
