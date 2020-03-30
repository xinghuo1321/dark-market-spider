import os
import random

from django.shortcuts import render
from django.http import HttpResponse

from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Pie, Page, Graph
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig

from marketWeb.settings import BASE_DIR
from nightmare.views import seller_chart, product_chart, country_chart, category_chart, seller_product_chart, \
    tag_words_chart
from post.models import Member, Post, Classification

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates', 'charts')))


def post_html(request, post_id):
    post_id = '{}.html'.format(post_id)
    print(post_id)
    return render(request, post_id)


def post_css(request):
    return render(request, 'styles/style.css')


def chart(request, chart_name):
    # TODO 各类别商品数量分析使用百分比显示, 各类别商品销售数量, 各类别对应用户数量

    # TODO 用户购买额, 出售额, 用户发布的商品 Graph()

    # TODO 所有爬虫的信息统计(包括 中文暗网,等等)
    if chart_name == 'classification':
        return HttpResponse(classification_chart())
    elif chart_name == 'member':
        return HttpResponse(member_chart())
    elif chart_name == 'member_post':
        return HttpResponse(member_post_chart())

    elif chart_name == 'seller':
        return HttpResponse(seller_chart())
    elif chart_name == 'product':
        return HttpResponse(product_chart())
    elif chart_name == 'country':
        return HttpResponse(country_chart())
    elif chart_name == 'category':
        return HttpResponse(category_chart())
    elif chart_name == 'seller_product':
        return HttpResponse(seller_product_chart())
    elif chart_name == 'tag_words':
        return HttpResponse(tag_words_chart())


def classification_chart():
    # 各类别商品数量分析使用饼图显示

    xaxis = [
        '帖子数',
        '交易量',
        '成交额(美元)',
    ]
    bar = (Bar(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')).add_xaxis(xaxis))
    pie_list = [[], [], []]
    for c in Classification.objects.all():
        # yaxis_values:'商品数量','已售商品数量','销售额()'
        yaxis_values = [0, 0, 0]
        posts = Post.objects.filter(classification=c)
        for post in posts:
            yaxis_values[0] += 1
            yaxis_values[1] += post.trade_number
            yaxis_values[2] += post.trade_number * post.dollar_price
        pie_list[0].append([c.name, yaxis_values[0]])
        pie_list[1].append([c.name, yaxis_values[1]])
        pie_list[2].append([c.name, yaxis_values[2]])
        bar.add_yaxis(c.name, yaxis_values)
    pie0 = Pie(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')
               ).add('', pie_list[0], radius=["40%", "75%"], ).set_global_opts(
        title_opts=opts.TitleOpts(title="各类别帖子数饼图"),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_top="15%", pos_left="100px"
        ),
    )
    pie1 = Pie(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')
               ).add('', pie_list[1]).set_global_opts(
        title_opts=opts.TitleOpts(title="各类别交易量饼图"),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_top="15%", pos_left="100px"
        ),
    )
    pie2 = Pie(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')
               ).add('', pie_list[2]).set_global_opts(
        title_opts=opts.TitleOpts(title="各类别成交额(美元)饼图"),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_top="15%", pos_left="100px"
        ),
    )
    bar.set_global_opts(
        # toolbox_opts=opts.ToolboxOpts(pos_top='25px', pos_left='0px'),
        legend_opts=opts.LegendOpts(),
        datazoom_opts=opts.DataZoomOpts(orient='vertical', range_start=0, range_end=100),

    ).set_series_opts(
        label_opts=opts.LabelOpts(
            position='top',
            horizontal_align='right',
            vertical_align='middle',
            rotate=-90),

    )

    page = Page(layout=Page.SimplePageLayout, js_host='../static/js/')
    page.add(bar, pie0, pie1, pie2)
    return page.render_embed()


def member_chart():
    purchase_num = []
    sell_num = []
    post_num = []

    for m in Member.objects.filter().order_by('-bitcoin_total_sale_amount')[:30]:
        sell_num.append([m.name, float(m.bitcoin_total_sale_amount)])
    for m in Member.objects.filter().order_by('-bitcoin_total_purchase_amount')[:30]:
        purchase_num.append([m.name, float(m.bitcoin_total_purchase_amount)])
    for m in Member.objects.filter().order_by('-on_sell_number')[:30]:
        post_num.append([m.name, m.on_sell_number])
    purchase_num_pie = Pie(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')
                           ).add('', purchase_num).set_global_opts(
        title_opts=opts.TitleOpts(title="购买总额(比特币)"),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_top="15%", pos_left="100px", type_='scroll'
        ),
    )
    sell_num_pie = Pie(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')
                       ).add('', sell_num).set_global_opts(
        title_opts=opts.TitleOpts(title="出售总额(比特币)"),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_top="15%", pos_left="100px", type_='scroll'
        ),
    )
    post_num_pie = Pie(init_opts=opts.InitOpts(js_host='../static/js/', width='1100px')
                       ).add('', post_num).set_global_opts(
        title_opts=opts.TitleOpts(title="发帖数"),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_top="15%", pos_left="100px", type_='scroll'
        ),
    )

    page = Page(layout=Page.SimplePageLayout, js_host='../static/js/')
    page.add(purchase_num_pie, sell_num_pie, post_num_pie)
    return page.render_embed()


def member_post_chart():
    point_color = ['#000',
                   '#0F0',
                   '#00F',
                   '#0FF',
                   '#F0F',
                   '#888',
                   ]
    member_post_link = []
    member_post_node = []
    for m in Member.objects.filter().order_by('-on_sell_number')[:20]:
        color = point_color[random.randint(0, len(point_color) - 1)]
        member_post_node.append({"name": m.name, "symbolSize": 10, "itemStyle": {"normal": {"color": color}}})
        for p in Post.objects.filter(member=m):
            member_post_node.append({
                "name": p.title,
                "symbolSize": 1,
                "itemStyle": {"normal": {"color": color}}
            })
            member_post_link.append({"source": m.name, "target": p.title})
    graph = (
        Graph(init_opts=opts.InitOpts(
            js_host='../static/js/', height='800%', width='1100px')
        ).add(
            "",
            member_post_node,
            member_post_link,
            repulsion=500,
            linestyle_opts=opts.LineStyleOpts(width=0.5, curve=0.3, opacity=0.7),
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="用户-帖子关系图"))
    )
    return graph.render_embed()
