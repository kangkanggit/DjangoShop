# Generated by Django 2.1.8 on 2019-07-25 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goods',
            name='goods_under',
            field=models.ImageField(default=1, upload_to=''),
        ),
    ]
