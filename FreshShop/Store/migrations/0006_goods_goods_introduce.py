# Generated by Django 2.1.8 on 2019-07-26 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0005_auto_20190725_2216'),
    ]

    operations = [
        migrations.AddField(
            model_name='goods',
            name='goods_introduce',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='商品的介绍'),
        ),
    ]
