# Generated by Django 2.1.8 on 2019-08-06 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0009_auto_20190729_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='goods',
            name='goods_less',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='商品的剩余数量'),
        ),
    ]
