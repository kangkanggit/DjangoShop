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




#商品加入购物车的功能
def adds_shop(request):
    pass

#商品的详情页
def show_shop(request,goods_id):
    goods = Goods.objects.filter(id=goods_id).first()#查询对应的商品
    goods_type = goods.goods_type#查询对应的商品类型
    return render(request,'buyer/show_shop.html',locals())
#商品的支付功能
def pay_order(request):
    money = request.GET.get('money')#获取订单的金额
    pass


#用户中心的编写






#详细页面的前端输入ajax验证
def ajax_show(request):
    result = {'status':'error','money':''}
    if request.method == 'GET':
        mun = request.GET.get('mun')
        mund = int(mun)
        goods_id = request.GET.get('goods_id')
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

#模板二页面
def base1(request):
    return render(request,'buyer/user_center.html')
# Create your views here.
