from django.db import models
from django.db.models import Manager

#卖家
class Seller(models.Model):
    username = models.CharField(max_length=32,verbose_name="用户名")
    password = models.CharField(max_length=32, verbose_name="密码")
    nickname = models.CharField(max_length=32, verbose_name="昵称",null=True,blank=True)
    phone = models.CharField(max_length=32, verbose_name="电话",null=True,blank=True)
    email = models.EmailField(verbose_name="邮箱",null=True,blank=True)
    picture = models.ImageField(upload_to="store/images", verbose_name="用户头像",null=True,blank=True)
    address = models.CharField(max_length=32, verbose_name="地址",null=True,blank=True)

    card_id = models.CharField(max_length=32, verbose_name="身份证号",null=True,blank=True)

#店铺类型
class StoreType(models.Model):
    store_type = models.CharField(max_length=32,verbose_name="类型名称")
    type_description = models.TextField(verbose_name="类型名称")

#店铺
class Store(models.Model):
    store_name = models.CharField(max_length=32, verbose_name="店铺名称")
    store_address = models.CharField(max_length=32,verbose_name="店铺地址")
    store_description = models.TextField(verbose_name="店铺描述")
    store_logo = models.ImageField(upload_to="store/images",verbose_name="店铺logo")
    store_phone = models.CharField(max_length=32,verbose_name="店铺电话")
    store_money = models.FloatField(verbose_name="店铺押金")

    user_id = models.IntegerField(verbose_name="店铺主人")
    type = models.ManyToManyField(to=StoreType,verbose_name="店铺类型")

#商品类型
class GoodsType(models.Model):
    name = models.CharField(max_length=32,verbose_name='商品的类型名')
    description = models.TextField(max_length=32,verbose_name='商品类型描述')
    picture = models.ImageField(upload_to='buyer/images',verbose_name='商品类型图片')
    aid = models.CharField(max_length=32, null=True, blank=True, verbose_name='样式id')

#商品
class Goods(models.Model):
    goods_name = models.CharField(max_length=32,verbose_name="商品名称")
    goods_price = models.FloatField(verbose_name="商品价格")
    goods_image = models.ImageField(upload_to="store/images", verbose_name="商品图片")
    goods_number = models.IntegerField(verbose_name="商品数量库存")
    goods_description = models.TextField(verbose_name="商品描述")
    goods_introduce = models.CharField(max_length=32,verbose_name='商品的介绍',null=True,blank=True)
    goods_date = models.DateField(verbose_name="出厂日期")
    goods_safeDate = models.IntegerField(verbose_name="保质期")
    goods_under = models.IntegerField(verbose_name="商品状态",default=1)#商品的上架下载状态
    goods_less = models.CharField(max_length=32,verbose_name='商品的剩余数量',null=True,blank=True)#商品的剩余数量。
    goods_type = models.ForeignKey(to=GoodsType,on_delete=models.CASCADE,verbose_name='商品类型',null=True,blank=True)
    store_id = models.ForeignKey(to=Store,on_delete=models.CASCADE,verbose_name="商品店铺")


#商品图片
class GoodsImg(models.Model):
    img_address = models.ImageField(upload_to="store/images",verbose_name="图片地址")
    img_description = models.TextField(max_length=32, verbose_name="图片描述")

    goods_id = models.ForeignKey(to = Goods,on_delete = models.CASCADE, verbose_name="商品id")

# Create your models here.
