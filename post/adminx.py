import xadmin
from xadmin import views
from post.models import Image, Member, Post, Classification
from django.utils.html import format_html
from marketWeb.settings import RUN_SERVER_IP, RUN_SERVER_PORT, TRANSFER_PROTOCOL


class PostAdmin(object):
    list_display = ['title', 'member', 'publish_date', 'classification', 'trade_number', 'remain_number',
                    'bitcoin_price', 'dollar_price', 'view_number',
                    'show_url']
    search_fields = ['title', 'content',
                     'classification__name', 'member__name']
    list_editable = []
    readonly_fields = ['id',
                       'publish_date',
                       'member',
                       'classification',
                       'title',
                       'bitcoin_price',
                       'view_number',
                       'protect_days',
                       'relative_url',
                       'trade_id',
                       'dollar_price',
                       'trade_type',
                       'trade_status',
                       'trade_number',
                       'goods_number',
                       'remain_number',
                       'content',
                       'html_path']
    list_filter = readonly_fields

    def show_url(self, obj):
        return format_html(
            '<a href="{}://{}:{}/'.format(TRANSFER_PROTOCOL, RUN_SERVER_IP, RUN_SERVER_PORT) +
            '{url}" target="_blank">{url}</a>',
            url=obj.html_path
        )

    show_url.short_description = '离线网页'

    redirect = True


class MemberAdmin(object):
    list_display = [
        'id',
        'name',
        'register_date',
        'bitcoin_total_sale_amount',
        'bitcoin_total_purchase_amount',
        'on_sell_number',
        'seller_last_online_date']
    search_fields = [
        'name',
        'bitcoin_total_sale_amount',
        'bitcoin_total_purchase_amount',
        'on_sell_number',
    ]
    readonly_fields = ['id',
                       'name',
                       'register_date',
                       'bitcoin_total_sale_amount',
                       'bitcoin_total_purchase_amount',
                       'on_sell_number',
                       'seller_last_online_date']
    list_filter = readonly_fields


class ClassificationAdmin(object):
    list_display = ['id', 'name']
    readonly_fields = list_display
    hidden_menu = True
    list_filter = readonly_fields


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


class GlobalSettings(object):
    site_title = '暗网爬虫系统'
    site_footer = 'dark spider'
    menu_style = 'accordion'


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(Member, MemberAdmin)
xadmin.site.register(Classification, ClassificationAdmin)
xadmin.site.register(Post, PostAdmin)
