import os
import random

from django.db.models import Q
from pyecharts import options as opts
from django.shortcuts import render
from pyecharts.charts import Pie, Page, Graph, WordCloud, Map
from pyecharts.globals import SymbolType

from nightmare.models import Seller, Product, ProductShipsFrom, Country, ProductShipsTo, Category, ProductTag, Tag


def nightmare_html(request, html_name):
    return render(request, os.path.join('nightmare', html_name.replace(' ', '%20')))


def nightmare_css(request, css_name):
    return render(request, os.path.join('nightmare', 'css', css_name))


def seller_chart():
    follower_num = []
    order_num = []
    for s in Seller.objects.order_by('-order_num')[:30]:
        order_num.append([s.name, s.order_num])

    for s in Seller.objects.filter().order_by('-followers_num')[:30]:
        follower_num.append([s.name, s.followers_num])

    follower_num_pie = Pie(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')
                           ).add('', follower_num, radius=["10%", "75%"],
                                 # center=["25%", "50%"],
                                 rosetype="radius", ).set_global_opts(
        title_opts=opts.TitleOpts(title="订阅数"),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_top="15%", pos_left="100px", type_='scroll'
        ),
    )
    order_num_pie = Pie(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')
                        ).add('', order_num, radius=["10%", "75%"],
                              # center=["25%", "50%"],
                              rosetype="radius", ).set_global_opts(
        title_opts=opts.TitleOpts(title="订单数"),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_top="15%", pos_left="100px", type_='scroll'
        ),
    )

    page = Page(layout=Page.SimplePageLayout, js_host='../static/js/')
    page.add(order_num_pie, follower_num_pie)
    return page.render_embed()


def product_chart():
    view_num = []
    for p in Product.objects.order_by('-view_num')[:30]:
        view_num.append([p.title[:20], p.view_num])

    view_num_pie = Pie(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')
                       ).add('', view_num).set_global_opts(
        title_opts=opts.TitleOpts(title="查看数"),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_top="15%", pos_left="100px", type_='scroll'
        ),
    )
    return view_num_pie.render_embed()


def country_chart():
    from_num = []
    to_num = []
    max_num = 0
    for c in Country.objects.filter(Q(to_number__gt=0) | Q(from_number__gt=0)).order_by('-to_number'):
        to_num.append([c.name, c.to_number])
        from_num.append([c.name, c.from_number])
        if c.to_number + c.from_number > max_num and c.name != 'WorldWide':
            max_num = c.to_number + c.from_number

    from_num = sorted(from_num, key=lambda d: d[1], reverse=True)

    from_num_pie = Pie(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')
                       ).add('', from_num).set_global_opts(
        title_opts=opts.TitleOpts(title="发货地址"),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_top="15%", pos_left="100px", type_='scroll'
        ),
    )
    to_num_pie = Pie(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')
                     ).add('', to_num).set_global_opts(
        title_opts=opts.TitleOpts(title="收货地址"),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_top="15%", pos_left="100px", type_='scroll'
        ),
    )

    c = (
        Map(init_opts=opts.InitOpts(width='1100px', height='550px', js_host='../static/js/'))
            .add("收货地址", to_num, "world")
            .add("发货地址", from_num, "world")
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
            title_opts=opts.TitleOpts(title="收发货地址"),
            visualmap_opts=opts.VisualMapOpts(max_=max_num, pos_top='50px'),
        )
    )

    page = Page(layout=Page.SimplePageLayout, js_host='../static/js/')
    page.add(c, from_num_pie, to_num_pie)
    return page.render_embed()


def category_chart():
    category_num = []
    for c in Category.objects.all():
        category_num.append([c.name, c.product_number])

    category_num_pie = Pie(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')
                           ).add('', category_num).set_global_opts(
        title_opts=opts.TitleOpts(title="类别商品数量"),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_top="15%", pos_left="100px", type_='scroll'
        ),
    )
    return category_num_pie.render_embed()


def seller_product_chart():
    point_color = ['#000',
                   '#0F0',
                   '#00F',
                   '#0FF',
                   '#F0F',
                   '#888',
                   ]
    seller_product_link = []
    seller_product_node = []

    for s in Seller.objects.order_by('-order_num')[:10]:
        color = point_color[random.randint(0, len(point_color) - 1)]
        seller_product_node.append({"name": s.name, "symbolSize": 10, "itemStyle": {"normal": {"color": color}}})
        for p in Product.objects.filter(seller=s)[:10]:
            seller_product_node.append({
                    "name": p.title,
                    "symbolSize": 1,
                    "itemStyle": {"normal": {"color": color}}
                })
            seller_product_link.append({"source": s.name, "target": p.title})
    graph = (
        Graph(init_opts=opts.InitOpts(
            js_host='../static/js/', height='800%', width='1100px')
        ).add(
            "",
            seller_product_node,
            seller_product_link,
            repulsion=500,
            linestyle_opts=opts.LineStyleOpts(width=0.5, curve=0.3, opacity=0.7),
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="商家-产品关系图"))
    )
    return graph.render_embed()


def tag_words_chart():
    tag_words_dict = {}

    for t in Tag.objects.order_by('-number')[:300]:
        tag_words_dict[t.name.lower()] = tag_words_dict.get(t.name.lower(), 0) + t.number
    word_cloud = WordCloud(
        init_opts=opts.InitOpts(
            height='700%', width='1100px',
            js_host='../static/js/',
        )
    ).add("", tag_words_dict.items(), word_size_range=[20, 100], shape=SymbolType.RECT)
    return word_cloud.render_embed()
