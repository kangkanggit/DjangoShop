from django.shortcuts import render
from django.http import JsonResponse
from django.http import  HttpResponseRedirect

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
    if goods_type:#如果存在
        goods_list = goods_type.goods_set.filter(goods_under=1)#返回在线的商品
        goods_first = goods_type.goods_set.filter(goods_under=1).first()#返回第一个商品
    return render(request,'buyer/good_list.html',locals())




#商品加入购物车的功能(需要改进)
def adds_car(request):
    goods_list = []
    if request.method == "GET":
        goods_id = request.GET.get('goods_id')
        goods = Goods.objects.filter(id=goods_id).first()#获取对应的商品
        print(goods)
        return render(request,'buyer/car.html',locals())
    return render(request,'buyer/car.html')



#商品的详情页
def show_shop(request,goods_id):
    goods = Goods.objects.filter(id=goods_id).first()#查询对应的商品
    goods_type = goods.goods_type#查询对应的商品类型
    return render(request,'buyer/show_shop.html',locals())

#商品的提交订单页面
def pay_order(request):
    if request.method == "GET":
        number = request.GET.get('number')#获取价格
        goods_id = request.GET.get('goods_id')#获取物品id
        goods = Goods.objects.filter(id=goods_id).first()#获取购买的商品
        # print(goods)
        user_id = request.COOKIES.get('user_id')#获取对应的用户
        buyer = Buyer.objects.filter(id=user_id).first()  # 查找对应的用户
        adds_list = buyer.address_set.all()  # 查找用户对应的地址
        return render(request, 'buyer/play_order.html',locals())
    return render(request,'buyer/play_order.html')


#支付功能
def pay_money(request):
    if request.method == "GET":
        money = request.GET.get('money')
        order_id = request.GET.get('order')
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
            subject="西瓜",  # 交易主题
            return_url="http://10.10.21.75:8000/Buyer/user_order/",
            notify_url="http://10.10.21.75:8000/Buyer/user_order/",
        )

        return HttpResponseRedirect("https://openapi.alipaydev.com/gateway.do?" + order_string)



#用户中心的编写
#个人信息页面
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

#编写订单页面(需要开发)
def user_order(request):
    return render(request,'buyer/user_order.html')

#收货地址页面
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
            goods_number = goods_mun.goods_number
            if munsd < goods_number:
                result['status'] = 'success'
                result['number'] = munsd+1
                result['money'] = (goods_mun.goods_price) * (munsd+1)
            else:
                result['number'] = goods_mun
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
        print(munsd)
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

#模板页面
def base(request):
    return render(request,'buyer/base.html')

# Create your views here.
