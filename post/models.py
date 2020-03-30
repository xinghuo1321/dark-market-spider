# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Classification(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='类别ID')
    name = models.CharField(max_length=100, verbose_name='类别名', default='')

    class Meta:
        db_table = 'classification'
        verbose_name_plural = '类别'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.name


class Image(models.Model):
    path = models.CharField(primary_key=True, max_length=255, verbose_name='图片地址')
    post = models.ForeignKey('Post', models.DO_NOTHING, verbose_name='帖子', default='')
    url = models.CharField(max_length=255, verbose_name='图片链接')

    class Meta:
        db_table = 'image'
        verbose_name_plural = '图片'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.path


class Member(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='用户ID')
    name = models.CharField(max_length=100, verbose_name='用户名', default='')
    register_date = models.DateField(verbose_name='注册日期')
    bitcoin_total_sale_amount = models.DecimalField(max_digits=10, decimal_places=6, verbose_name='总出售额(比特币)')
    bitcoin_total_purchase_amount = models.DecimalField(max_digits=10, decimal_places=6, verbose_name='总购买额(比特币)')
    on_sell_number = models.IntegerField(verbose_name='在售单数')
    seller_last_online_date = models.DateField(verbose_name='最后在线日期')

    class Meta:
        db_table = 'member'
        verbose_name_plural = '用户'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.name


class Post(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='ID')
    publish_date = models.DateField(verbose_name='发布日期')
    member = models.ForeignKey(Member, models.DO_NOTHING, verbose_name='发布者', default='')
    classification = models.ForeignKey(Classification, models.DO_NOTHING, verbose_name='类别', default='')
    title = models.CharField(max_length=255, verbose_name='标题')
    bitcoin_price = models.DecimalField(max_digits=10, decimal_places=6, verbose_name='价格(比特币)')
    view_number = models.IntegerField(verbose_name='浏览数')
    protect_days = models.IntegerField(verbose_name='保护时长(天)')
    relative_url = models.CharField(max_length=255, verbose_name='URL pathname')
    trade_id = models.IntegerField(verbose_name='交易编号')
    dollar_price = models.IntegerField(verbose_name='价格(美元)')
    trade_type = models.CharField(max_length=50, verbose_name='交易类型')
    trade_status = models.CharField(max_length=50, verbose_name='交易状态')
    trade_number = models.IntegerField(verbose_name='成交量')
    goods_number = models.IntegerField(verbose_name='出售数量')
    remain_number = models.IntegerField(verbose_name='剩余量')
    content = models.TextField(verbose_name='内容')
    html_path = models.CharField(max_length=255, verbose_name='离线网页')

    class Meta:
        db_table = 'post'
        verbose_name_plural = '帖子'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.title
