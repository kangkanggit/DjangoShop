# Generated by Django 2.1.8 on 2019-07-31 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Buyer', '0008_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='goods_live',
            field=models.IntegerField(default=0, verbose_name='购物车的状态'),
        ),
    ]