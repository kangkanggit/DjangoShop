from rest_framework import serializers
from Store.models import *

class UserSerializer(serializers.HyperlinkedModelSerializer):
    #声明数据
    class Meta: #元素
        model = Goods#要接口的数据模型
        fields = ['goods_name','goods_price','goods_number'
                  ,'goods_date','goods_safeDate','id','goods_less']#要返回的字段

class GoodsTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:#字段
        model = GoodsType#要获取的表
        fields = ['name','description']


