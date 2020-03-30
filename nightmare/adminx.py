import xadmin
from django.utils.html import format_html

from nightmare.models import SiteData, VerifiedUser, FeedbackStatistics, Seller, Category, Product, ProductFeedBack, \
    SellerFeedback, FeedbackLeftAsSeller, Country, Tag, ProductShipsFrom, ProductShipsTo, ProductTag

from marketWeb.settings import RUN_SERVER_IP, RUN_SERVER_PORT, TRANSFER_PROTOCOL


class SiteDataAdmin(object):
    list_display = [
        'datetime',
        'active_user_num',
        'active_seller_num',
        'currency'
    ]
    search_fields = []
    list_editable = []
    readonly_fields = ['datetime', 'active_user_num',
                       'active_seller_num', 'currency']
    list_filter = readonly_fields


class VerifiedUserAdmin(object):
    hidden_menu = True
    list_display = ['name', 'sales', 'rating']
    search_fields = ['name']
    list_editable = []
    readonly_fields = ['name', 'sales', 'rating']
    list_filter = readonly_fields


class FeedbackStatisticsAdmin(object):
    hidden_menu = True
    list_display = ['one_month_positive_feedback_num',
                    'one_month_negative_feedback_num',
                    'six_month_positive_feedback_num',
                    'six_month_negative_feedback_num',
                    'since_join_positive_feedback_num',
                    'since_join_negative_feedback_num']
    search_fields = []
    list_editable = []
    readonly_fields = ['one_month_positive_feedback_num',
                       'one_month_negative_feedback_num',
                       'six_month_positive_feedback_num',
                       'six_month_negative_feedback_num',
                       'since_join_positive_feedback_num',
                       'since_join_negative_feedback_num']
    list_filter = readonly_fields


class SellerAdmin(object):
    list_display = [
        'name',
        'order_num',
        'rating',
        'trust_level',
        'verified_user',
        'live_jabber_notification',
        'level',
        'followers_num',
        'member_since',
        'feedback_statistics',
        'icq',
        'jabber',
        'show_url'
    ]
    search_fields = [
        'name',
        'verified_user__name',
        'about',
        'chinese_about',
        'pgp',
        'news',
        'icq',
        'jabber',
    ]
    list_editable = []
    readonly_fields = ['url',
                       'name',
                       'order_num',
                       'rating',
                       'trust_level',
                       'verified_user',
                       'live_jabber_notification',
                       'level',
                       'followers_num',
                       'member_since',
                       'feedback_statistics',
                       'about',
                       'chinese_about',
                       'pgp',
                       'news',
                       'image_url',
                       'image_path',
                       'icq',
                       'jabber',
                       'html_path']
    list_filter = readonly_fields

    def show_url(self, obj):
        return format_html(
            '<a href="{}://{}:{}/'.format(TRANSFER_PROTOCOL, RUN_SERVER_IP, RUN_SERVER_PORT) +
            '{url}" target="_blank">html</a>', url=obj.html_path
        )

    show_url.short_description = '离线网页'

    redirect = True


class CategoryAdmin(object):
    # hidden_menu = True
    list_display = ['name',
                    'product_number',
                    'url', ]
    search_fields = ['name', ]
    list_editable = []
    readonly_fields = ['name',
                       'url',
                       'page_number',
                       'product_number']
    list_filter = readonly_fields


class ProductAdmin(object):
    list_display = [
        'title',
        'chinese_title',
        'seller',
        'category',
        'quantity_left',
        'view_num',
        'payment',
        'visibility',
        'price',
        'ends_in',
        'show_url']
    search_fields = [
        'title',
        'chinese_title',
        'seller__name',
        'category__name',
        'quantity_left',
        'payment',
        'visibility',
        'description',
        'chinese_description',
        'refund_policy',
        'terms_conditions',
    ]
    list_editable = []
    readonly_fields = ['url',
                       'title',
                       'chinese_title',
                       'seller',
                       'category',
                       'quantity_left',
                       'view_num',
                       'payment',
                       'visibility',
                       'price',
                       'description',
                       'chinese_description',
                       'refund_policy',
                       'terms_conditions',
                       'ends_in',
                       'html_path']
    list_filter = readonly_fields

    def show_url(self, obj):
        return format_html(
            '<a href="{}://{}:{}/'.format(TRANSFER_PROTOCOL, RUN_SERVER_IP, RUN_SERVER_PORT) +
            '{url}" target="_blank">html</a>',
            url=obj.html_path
        )

    show_url.short_description = '离线网页'

    redirect = True


class ProductFeedBackAdmin(object):
    list_display = [
        'content',
        'product',
        'buyer',
        'seller',
        'negative_or_positive',
        'price',
        'rating',

        'datetime']
    search_fields = ['product__title',
                     'buyer__name',
                     'content',
                     'seller__name', ]
    list_editable = []
    readonly_fields = ['product',
                       'buyer',
                       'negative_or_positive',
                       'price',
                       'rating',
                       'content',
                       'seller',
                       'datetime']
    list_filter = ['product',
                   'buyer__name',
                   'negative_or_positive',
                   'price',
                   'rating',
                   'content',
                   'seller',
                   'datetime']


class SellerFeedbackAdmin(object):
    show_full_result_count = False
    list_display = [
        'content',
        'buyer',
        'seller',
        'negative_or_positive',

        'price',
        'datetime',
        'rating',
    ]
    search_fields = [
        'content',
        'buyer__name',
        'seller__name'
    ]
    list_editable = []
    readonly_fields = ['negative_or_positive',
                       'content',
                       'buyer',
                       'price',
                       'datetime',
                       'rating',
                       'product_url',
                       'seller', ]
    list_filter = ['negative_or_positive',
                   'content',
                   'buyer__name',
                   'price',
                   'datetime',
                   'rating',
                   'product_url',
                   'seller__name', ]


class FeedbackLeftAsSellerAdmin(object):
    list_display = [
        'content', 'seller', 'buyer',
        'negative_or_positive',
        'price',
        'datetime',
        'rating',
    ]
    search_fields = [
        'content',
        'buyer__name',
        'seller__name']
    list_editable = []
    readonly_fields = ['negative_or_positive',
                       'content',
                       'seller',
                       'buyer',
                       'price',
                       'datetime',
                       'rating', ]
    list_filter = ['negative_or_positive',
                   'content',
                   'seller__name',
                   'buyer__name',
                   'price',
                   'datetime',
                   'rating', ]


class ProductTagAdmin(object):
    list_display = [
        'product', 'tag'
    ]
    search_fields = ['product__title', 'tag__name']
    list_editable = []
    readonly_fields = ['product', 'tag']
    list_filter = ['product__title', 'tag__name']


class TagAdmin(object):
    # hidden_menu = True
    show_full_result_count = False
    list_display = [
        'name',
        'number'
    ]
    search_fields = list_display
    list_editable = []
    readonly_fields = list_display
    list_filter = readonly_fields


class CountryAdmin(object):
    hidden_menu = True
    list_display = [
        'name'
    ]
    search_fields = []
    list_editable = []
    readonly_fields = ['name']
    list_filter = readonly_fields


class ProductShipsFromAdmin(object):
    list_display = [
        'product', 'country'
    ]
    search_fields = ['product__title', 'country__name']
    list_editable = []
    readonly_fields = ['product', 'country']
    list_filter = ['product__title', 'country']


class ProductShipsToAdmin(object):
    list_display = [
        'product', 'country'
    ]
    search_fields = ['product__title', 'country__name']
    list_editable = []
    readonly_fields = ['product', 'country']
    list_filter = ['product__title', 'country']


xadmin.site.register(Product, ProductAdmin)
xadmin.site.register(Seller, SellerAdmin)
xadmin.site.register(SiteData, SiteDataAdmin)
xadmin.site.register(VerifiedUser, VerifiedUserAdmin)
xadmin.site.register(FeedbackStatistics, FeedbackStatisticsAdmin)
xadmin.site.register(Category, CategoryAdmin)
xadmin.site.register(ProductFeedBack, ProductFeedBackAdmin)
xadmin.site.register(SellerFeedback, SellerFeedbackAdmin)
xadmin.site.register(FeedbackLeftAsSeller, FeedbackLeftAsSellerAdmin)
xadmin.site.register(Country, CountryAdmin)
xadmin.site.register(Tag, TagAdmin)
xadmin.site.register(ProductShipsFrom, ProductShipsFromAdmin)
xadmin.site.register(ProductShipsTo, ProductShipsToAdmin)
xadmin.site.register(ProductTag, ProductTagAdmin)
