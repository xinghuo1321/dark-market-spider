from django.db import models
from django.utils import timezone


class Buyer(models.Model):
    name = models.CharField(max_length=50, verbose_name='买家', default='', primary_key=True)

    class Meta:
        verbose_name_plural = '买家'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.name


class SiteData(models.Model):
    # date 每10分钟添加一次
    # id = models.IntegerField(verbose_name='ID', primary_key=True, default=0)
    datetime = models.DateTimeField(verbose_name='添加时间', default=timezone.now, primary_key=True)
    active_user_num = models.IntegerField(verbose_name='在线用户数')
    active_seller_num = models.IntegerField(verbose_name='在线商家数')
    # CURRENCY(models.Model): USD(11274.26
    currency = models.FloatField(verbose_name='Currency')

    class Meta:
        verbose_name_plural = '网址数据'
        verbose_name = verbose_name_plural

    def __str__(self):
        return ''.format(self.datetime)


class VerifiedUser(models.Model):
    name = models.CharField(max_length=100, verbose_name='名', default='')
    sales = models.IntegerField(verbose_name='订单数')
    rating = models.FloatField(verbose_name='星级')

    class Meta:
        verbose_name_plural = '用户组'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.name


class FeedbackStatistics(models.Model):
    one_month_positive_feedback_num = models.IntegerField(verbose_name='过去一个月商家收到的正面评价数')
    one_month_negative_feedback_num = models.IntegerField(verbose_name='过去一个月商家收到的负面评价数')
    six_month_positive_feedback_num = models.IntegerField(verbose_name='过去六个月商家收到的正面评价数')
    six_month_negative_feedback_num = models.IntegerField(verbose_name='过去六个月商家收到的负面评价数')
    since_join_positive_feedback_num = models.IntegerField(verbose_name='商家收到的正面评价总数')
    since_join_negative_feedback_num = models.IntegerField(verbose_name='商家收到的负面评价总数')

    class Meta:
        verbose_name_plural = '评价分析'
        verbose_name = verbose_name_plural

    def __str__(self):
        return '评价分析'


class Seller(models.Model):
    url = models.CharField(max_length=255, verbose_name='商家URL', default='', primary_key=True)
    name = models.CharField(max_length=100, verbose_name='商家名')
    order_num = models.IntegerField(verbose_name='订单数')
    rating = models.FloatField(verbose_name='星级')
    trust_level = models.IntegerField(verbose_name='可信度')
    verified_user = models.ForeignKey(VerifiedUser, on_delete=models.DO_NOTHING, verbose_name='所属商家组', blank=True,
                                      null=True)
    live_jabber_notification = models.BooleanField(verbose_name='jabber 在线')
    level = models.CharField(verbose_name='用户等级', max_length=50)
    followers_num = models.IntegerField(verbose_name='粉丝数')
    member_since = models.DateField(verbose_name='注册时间')
    feedback_statistics = models.ForeignKey(FeedbackStatistics, on_delete=models.DO_NOTHING,
                                            verbose_name='商家评价分析')
    about = models.TextField(verbose_name='About')
    chinese_about = models.TextField(verbose_name='关于', default='')
    pgp = models.TextField(verbose_name='PGP', default='')
    news = models.TextField(verbose_name='新闻')
    image_url = models.CharField(max_length=255, verbose_name='图片URL', default='')
    image_path = models.CharField(max_length=255, verbose_name='图片存储地址', default='')
    icq = models.CharField(verbose_name='icq', max_length=200, default='')
    jabber = models.CharField(verbose_name='jabber', max_length=200, default='')
    html_path = models.CharField(max_length=255, verbose_name='html存储地址', default='')

    class Meta:
        verbose_name_plural = '商家'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='类别名', primary_key=True)
    url = models.CharField(max_length=255, verbose_name='URL')
    page_number = models.IntegerField(verbose_name='总页数')
    product_number = models.IntegerField(verbose_name='产品数', default=0)

    class Meta:
        verbose_name_plural = '分类'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='title', default='')
    chinese_title = models.CharField(max_length=255, verbose_name='标题', default='')
    url = models.CharField(max_length=255, verbose_name='产品URL', primary_key=True)
    seller = models.ForeignKey(Seller, on_delete=models.DO_NOTHING, verbose_name='商家')
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, verbose_name='类别')
    quantity_left = models.IntegerField(verbose_name='剩余数', default=0)
    view_num = models.IntegerField(verbose_name='浏览数', default=0)
    payment = models.CharField(max_length=50, verbose_name='支付', default='')
    visibility = models.CharField(max_length=50, verbose_name='可见度', default='')
    ends_in = models.CharField(max_length=50, verbose_name='Ends In', default='')
    price = models.FloatField(verbose_name='价格')
    description = models.TextField(verbose_name='description')
    chinese_description = models.TextField(verbose_name='描述', default='')
    refund_policy = models.TextField(verbose_name='退款政策')
    terms_conditions = models.TextField(verbose_name='条款和条件')
    html_path = models.CharField(max_length=255, verbose_name='html存储地址', default='')

    class Meta:
        verbose_name_plural = '产品'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    url = models.CharField(max_length=255, verbose_name='图片URL', primary_key=True)
    path = models.CharField(max_length=255, verbose_name='图片存储地址')
    product_url = models.CharField(max_length=255, verbose_name='产品URL', default='')

    class Meta:
        verbose_name_plural = '产品图片'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.path


class ProductFeedBack(models.Model):
    product = models.ForeignKey(Product, models.DO_NOTHING, verbose_name='产品')
    buyer = models.ForeignKey(Buyer, on_delete=models.DO_NOTHING, verbose_name='买家', null=True, blank=True)
    negative_or_positive = models.BooleanField(verbose_name='正面评价或负面评价', default=True)
    price = models.FloatField(verbose_name='价格')
    rating = models.IntegerField(verbose_name='星级')
    content = models.TextField(verbose_name='内容')
    seller = models.ForeignKey(Seller, on_delete=models.DO_NOTHING, verbose_name='商家', null=True, blank=True)
    datetime = models.DateTimeField(verbose_name='日期时间', default=timezone.now)

    class Meta:
        verbose_name_plural = '产品评价'
        verbose_name = verbose_name_plural

    def __str__(self):
        return '产品评价'


class SellerFeedback(models.Model):
    negative_or_positive = models.BooleanField(verbose_name='正面评价或负面评价', default=True)
    content = models.TextField(verbose_name='内容')
    buyer = models.ForeignKey(Buyer, on_delete=models.DO_NOTHING, verbose_name='买家', null=True, blank=True)
    price = models.FloatField(verbose_name='价格')
    datetime = models.DateTimeField(verbose_name='日期时间')
    rating = models.IntegerField(verbose_name='星级')
    product_url = models.CharField(max_length=255, verbose_name='产品URL', default='')
    seller = models.ForeignKey(Seller, on_delete=models.DO_NOTHING, verbose_name='商家')

    class Meta:
        verbose_name_plural = '商家收到的评价'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.buyer.name


class FeedbackLeftAsSeller(models.Model):
    negative_or_positive = models.BooleanField(verbose_name='正面评价或负面评价', default=True)
    content = models.TextField(verbose_name='内容')
    seller = models.ForeignKey(Seller, on_delete=models.DO_NOTHING, verbose_name='商家')
    buyer = models.ForeignKey(Buyer, on_delete=models.DO_NOTHING, verbose_name='买家', null=True, blank=True)
    price = models.FloatField(verbose_name='价格')
    datetime = models.DateTimeField(verbose_name='日期时间')
    rating = models.IntegerField(verbose_name='星级')

    class Meta:
        verbose_name_plural = '商家留下的评价'
        verbose_name = verbose_name_plural

    def __str__(self):
        return 'Seller:{} Buyer:{}'.format(self.seller.name, self.buyer.name)


class Tag(models.Model):
    name = models.CharField(max_length=150, verbose_name='标签名', default='', primary_key=True)
    number = models.IntegerField(verbose_name='出现次数', default=0)

    class Meta:
        verbose_name_plural = '标签'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=50, verbose_name='国家名', default='', primary_key=True)
    from_number = models.IntegerField(default=0, verbose_name='发货地次数')
    to_number = models.IntegerField(default=0, verbose_name='收货地次数')

    class Meta:
        verbose_name_plural = '国家'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, verbose_name='产品')
    tag = models.ForeignKey(Tag, on_delete=models.DO_NOTHING, verbose_name='标签')

    class Meta:
        verbose_name_plural = '产品标签'
        verbose_name = verbose_name_plural

    def __str__(self):
        return '{}-{}'.format(self.product.title, self.tag.name)


class ProductShipsFrom(models.Model):
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, verbose_name='产品')
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, verbose_name='国家')

    class Meta:
        verbose_name_plural = '产品发货地'
        verbose_name = verbose_name_plural

    def __str__(self):
        return '{}-{}'.format(self.product.title, self.country.name)


class ProductShipsTo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, verbose_name='产品')
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, verbose_name='国家')

    class Meta:
        verbose_name_plural = '产品收货地'
        verbose_name = verbose_name_plural

    def __str__(self):
        return '{}-{}'.format(self.product.title, self.country.name)
