import codecs
import datetime
import os
import re
import shutil

import MySQLdb

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome, ChromeOptions
import time

from TorProxy.tor_controller import restart_tor
from settings import MYSQL_HOST, MYSQL_USER, \
    MYSQL_PASSWORD, CHINESE_FORUM_MYSQL_DATABASE_NAME, USERNAME, PASSWORD, BASE_DIR, IMAGE_DIR, HTML_DIR, HTML_IMAGE_DIR


class Classification:
    id = None
    name = None

    def __init__(self, id, name):
        self.id = int(id)
        self.name = name

    def get_insert_sql(self):
        sql = '''
              INSERT INTO classification(
              {}, {})
              VALUES(%s, %s)
              '''
        params = (
            self.id, self.name
        )
        if execute_mysql('SELECT COUNT(*) from classification where id=%s', [self.id]).fetchone()[0] == 0:
            return sql, params
        else:
            return None, None


class Image:
    path = None
    post_id = None
    url = None

    def __init__(self, path, post_id, url):
        self.post_id = post_id
        self.url = url
        self.path = path

    def get_insert_sql(self):
        sql = '''
              INSERT INTO image(
              path, post_id, url)
              VALUES(%s, %s, %s)
              '''
        params = (
            self.path, self.post_id, self.url
        )
        if execute_mysql('SELECT COUNT(*) from image where path=%s', [self.path]).fetchone()[0] == 0:
            return sql, params
        else:
            return None, None


class Member:
    # 账户编号
    id = None
    # 账号名称
    name = None
    # 注册时间
    register_date = None
    # 总出售额
    bitcoin_total_sale_amount = None
    # 总购买额
    bitcoin_total_purchase_amount = None
    # 在售单数
    on_sell_number = None
    # 商家最后在线时间
    seller_last_online_date = None

    def __init__(self, id, name, register_date, bitcoin_total_sale_amount, bitcoin_total_purchase_amount,
                 seller_last_online_date, on_sell_number):
        self.id = id
        self.name = name
        self.register_date = '{} 00:00'.format(register_date)
        self.bitcoin_total_sale_amount = bitcoin_total_sale_amount
        self.bitcoin_total_purchase_amount = bitcoin_total_purchase_amount
        self.seller_last_online_date = '{}-{}'.format(
            datetime.datetime.now().year, seller_last_online_date)
        self.on_sell_number = on_sell_number

    def get_insert_sql(self):

        if execute_mysql('SELECT COUNT(*) from member where id=%s', [self.id]).fetchone()[0] == 0:
            sql = '''
                          INSERT INTO member(
                          id, name, register_date, 
                          bitcoin_total_sale_amount,bitcoin_total_purchase_amount, seller_last_online_date, 
                          on_sell_number)
                          VALUES(%s, %s, %s, %s, %s,%s, %s)
                          '''
            params = (
                self.id, self.name, self.register_date,
                self.bitcoin_total_sale_amount, self.bitcoin_total_purchase_amount, self.seller_last_online_date,
                self.on_sell_number
            )
        else:
            sql = '''
                    update member
                    set name=%s, 
                    register_date=%s, 
                    bitcoin_total_sale_amount=%s,
                    bitcoin_total_purchase_amount=%s,
                    seller_last_online_date=%s, 
                    on_sell_number=%s
                    where id=%s
                '''
            params = (
                self.name, self.register_date,
                self.bitcoin_total_sale_amount,
                self.bitcoin_total_purchase_amount,
                self.seller_last_online_date,
                self.on_sell_number,
                self.id
            )
        return sql, params


class Post:
    id = None
    # 发布时间
    publish_date = None
    # 发布人id
    member_id = None
    # 标题
    title = None
    # 比特币单价
    bitcoin_price = None
    # 关注度
    view_number = None
    # 保护期
    protect_days = None
    # 所属分类id
    classification_id = None
    # 相对URL
    relative_url = None
    # 交易编号
    trade_id = None
    # 美元单价
    dollar_price = None
    # 交易类型
    trade_type = None
    # 交易状态
    trade_status = None
    # 成交数量
    trade_number = None
    # 商品数量
    goods_number = None
    # 剩余数量
    remain_number = None
    # 详细内容
    content = None
    # HTML path
    html_path = None

    def __init__(self, publish_date, member_id, title,
                 bitcoin_price, view_number, protect_days,
                 classification_id, trade_id, dollar_price,
                 trade_type, trade_number, trade_status,
                 goods_number, remain_number, content, id
                 ):
        self.id = id
        self.publish_date = '{}-{}'.format(
            datetime.datetime.now().year, publish_date)
        self.member_id = member_id
        self.title = title
        self.bitcoin_price = float(bitcoin_price)
        self.view_number = int(view_number)
        self.protect_days = int(protect_days.strip('天'))
        self.classification_id = classification_id
        self.relative_url = r'/viewtopic.php?t={}'.format(self.id)

        self.trade_id = int(trade_id)
        self.dollar_price = float(dollar_price)
        self.trade_type = trade_type
        self.trade_status = trade_status
        self.trade_number = int(trade_number)
        try:
            self.goods_number = int(goods_number)
        except ValueError as _:
            self.goods_number = 999999
        try:
            self.remain_number = int(remain_number)
        except ValueError as _:
            self.remain_number = 999999
        self.content = content
        self.html_path = '{}/{}.html'.format(HTML_DIR, self.id)

    def get_insert_sql(self):
        sql = '''
              INSERT INTO post(
              id, publish_date, member_id, 
              title,bitcoin_price, view_number, 
              protect_days,classification_id, relative_url,
              trade_id, dollar_price, trade_type, 
              trade_status,trade_number,goods_number, 
              remain_number, content, html_path)
              VALUES(%s, %s, %s, %s, %s,%s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)
              '''
        params = (
            self.id, self.publish_date, self.member_id,
            self.title, self.bitcoin_price, self.view_number,
            self.protect_days, self.classification_id, self.relative_url,
            self.trade_id, self.dollar_price, self.trade_type,
            self.trade_status, self.trade_number, self.goods_number,
            self.remain_number, self.content, self.html_path
        )

        return sql, params


class Spider:
    driver = None
    main_url = None

    def __init__(self):
        options = ChromeOptions()
        # options.add_argument('download.default_directory={}'.format(IMAGE_DIR))
        prefs = {'download.default_directory': os.path.join(
            BASE_DIR, IMAGE_DIR)}
        options.add_experimental_option('prefs', prefs)
        # options.add_argument('headless')
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
        self.driver = Chrome(options=options)
        self.driver.maximize_window()

    def login(self):
        print('try to login...')
        self.driver.get(
            'http://almvdkg6vrpmkvk4.onion')
        start_time = time.time()
        while True:
            try:
                username = self.driver.find_element_by_css_selector(
                    '#username')
                username.send_keys(USERNAME)
                password = self.driver.find_element_by_css_selector(
                    '#password')
                password.send_keys(PASSWORD)
                submit = self.driver.find_element_by_xpath(
                    '//*[@id="login"]/div[1]/div/div/fieldset/dl[4]/dd/input[3]')
                submit.click()
            except NoSuchElementException as _:
                if time.time() - start_time > 20:
                    start_time = time.time()
                    restart_tor()
                    time.sleep(10)
                    self.driver.refresh()

            finally:
                if '/index.php' in self.driver.current_url or '暗网交易市场 - 网站首页' in self.driver.title:
                    self.main_url = re.match(r'(http://.*?.onion)/index.php', self.driver.current_url).groups()[
                        0]
                    print('login success')
                    return

    def check_main_url(self, url):
        if self.main_url not in url:
            main_url = re.match('(http://.*?.onion)/.*?', url)
            if main_url:
                self.main_url = main_url.groups()[0]

    def driver_get(self, url, download=False):
        time.sleep(0.1)
        self.check_main_url(self.driver.current_url)
        print('get {}'.format(url))
        self.driver.get(url)
        try:
            self.driver.find_element_by_tag_name('body').text
        except Exception as _:
            restart_tor()
            time.sleep(10)
            self.driver.refresh()
        finally:
            try:
                if '请点此处重新进入.' in self.driver.page_source:
                    self.driver.find_element_by_css_selector(
                        'body div table tbody tr:nth-child(4) td:nth-child(2) a').click()
            except Exception as _:
                pass
            if USERNAME not in self.driver.page_source and not download:
                # TODO
                self.login()
                self.check_main_url(self.driver.current_url)
                url = self.main_url + \
                    re.match(r'.*?\.onion(.*)', url).groups()[0]
                self.driver_get(url)
        self.check_main_url(self.driver.current_url)


class MasterSpider(Spider):

    def __init__(self):
        Spider.__init__(self)

    def get_classification_url(self):
        text = self.driver.page_source
        text = text.split(
            'class="text_index_top">分类</a>')[1].split('<td>使用</td>')[0]
        classification_list = re.findall(
            r'/pay/user_area.php\?q_ea_id=(\d+).*?class="text_index_top">(\w*)</a>',
            text
        )

        return classification_list

    def run_spider(self):
        # TODO 需要先运行TorProxy下面的run.bat
        self.login()
        for c_id, name in self.get_classification_url():
            url = self.main_url + '/pay/user_area.php?q_ea_id=' + c_id
            c = Classification(id=c_id, name=name)
            save_to_mysql(c)
            self.driver_get(url)
            self.get_classification_page(c_id)

    def get_classification_page(self, c_id):

        page_number = int(
            self.driver.find_elements_by_class_name('page_b1')[-1].text)

        # TODO for page in range(2, page_number + 1):
        for page in range(2, 5):
            try:
                table = self.driver.find_element_by_css_selector(
                    'body div div.bodydiv div table.m_area_a tbody')
            except NoSuchElementException as e:
                url = self.main_url + '/pay/user_area.php?q_ea_id=' + c_id
                self.driver_get(url)
                self.get_classification_page(c_id)
            classification_id = re.search(
                r'/pay/user_area.php\?q_ea_id=(\d+)', self.driver.current_url).groups()[0]
            tr_url_list = [[i.text, i.find_elements_by_tag_name('a')[1].get_attribute('href')] for i in
                           table.find_elements_by_tag_name('tr') if ':' in i.text]
            for tr, url in tr_url_list:
                self.get_post_page(tr, url, c_id)

            self.driver_get('{}/pay/user_area.php?q_ea_id={}&pagey={}#pagey'.format(self.main_url, classification_id,
                                                                                    page))

    def get_post_page(self, tr, url, c_id):
        print('get post page {}'.format(url))
        tmp_list = tr.strip(' 打开').split()
        publish_date = '{} {}'.format(tmp_list[1], tmp_list[2])
        classification_id = tmp_list[3]
        name = tmp_list[4]
        title = ' '.join(tmp_list[5:-3])
        bitcoin_price = tmp_list[-3]
        protect_days = tmp_list[-2]
        view_number = tmp_list[-1]
        post_id = int(re.search(r'/viewtopic.php\?t=(\d+)', url).groups()[0])
        if execute_mysql('SELECT COUNT(*) from post where id=%s', [post_id]).fetchone()[0] != 0:
            return

        self.driver_get(url)
        page_source = self.driver.page_source
        page_source = page_source.replace(
            './assets/css/',
            './css/'
        ).replace(
            './styles/se_square_left/theme/',
            './css/theme/'
        ).replace(
            '/pay/',
            './css/'
        )
        dollar_price = self.driver.find_element_by_css_selector(
            '#page-body ul form:nth-child(3) table tbody tr:nth-child(3) td:nth-child(4) span').text
        trade_type = self.driver.find_element_by_css_selector(
            '#page-body ul form:nth-child(3) table tbody tr:nth-child(5) td:nth-child(2)').text
        trade_status = self.driver.find_element_by_css_selector(
            '#page-body ul form:nth-child(3) table tbody tr:nth-child(7) td:nth-child(2)').text
        trade_number = self.driver.find_element_by_css_selector(
            '#page-body ul form:nth-child(3) table tbody tr:nth-child(7) td:nth-child(4)').text
        goods_number = self.driver.find_element_by_css_selector(
            '#page-body ul form:nth-child(3) table tbody tr:nth-child(9) td:nth-child(2)').text
        remain_number = self.driver.find_element_by_css_selector(
            '#page-body ul form:nth-child(3) table tbody tr:nth-child(9) td:nth-child(4)').text
        register_date = self.driver.find_element_by_css_selector(
            '#page-body ul table.v_table_2 tbody tr:nth-child(7) td:nth-child(2)').text
        bitcoin_total_sale_amount = self.driver.find_element_by_css_selector(
            '#page-body ul table.v_table_2 tbody tr:nth-child(5) td:nth-child(4)').text
        bitcoin_total_purchase_amount = self.driver.find_element_by_css_selector(
            '#page-body ul table.v_table_2 tbody tr:nth-child(7) td:nth-child(4)').text
        seller_last_online_date = self.driver.find_element_by_css_selector(
            '#page-body ul form:nth-child(3) table tbody tr:nth-child(7) td:nth-child(6)').text
        on_sell_number = self.driver.find_element_by_css_selector(
            '#page-body ul table.v_table_2 tbody tr:nth-child(3) td:nth-child(4)').text
        trade_id = self.driver.find_element_by_css_selector(
            '#page-body ul form:nth-child(3) table tbody tr:nth-child(3) td:nth-child(2)').text
        content = self.driver.find_element_by_class_name('content').text
        images = []
        for i in self.driver.find_elements_by_tag_name('img'):
            try:
                i_name = '{}_{}'.format(post_id, i.get_attribute('alt'))
                i_path = os.path.join(IMAGE_DIR, i_name)
                i_url = i.get_attribute('src')
                i_relative_url = re.match(
                    r'^.*?\.onion(/.*?)$', i_url).groups()[0]
                images.append([i_name, i_path, i_url, i_relative_url])
            except Exception as e:
                print(e.args)
        member_id = self.driver.find_element_by_css_selector(
            '#page-body ul table.v_table_2 tbody tr:nth-child(5) td:nth-child(2)').text
        post = Post(
            id=post_id,
            publish_date=publish_date,
            member_id=member_id,
            title=title,
            bitcoin_price=bitcoin_price,
            view_number=view_number,
            protect_days=protect_days,
            classification_id=c_id,
            trade_id=trade_id,
            dollar_price=dollar_price,
            trade_type=trade_type,
            trade_status=trade_status,
            trade_number=trade_number,
            goods_number=goods_number,
            remain_number=remain_number,
            content=content,
        )
        member = Member(
            id=member_id,
            name=name,
            register_date=register_date,
            bitcoin_total_sale_amount=bitcoin_total_sale_amount,
            bitcoin_total_purchase_amount=bitcoin_total_purchase_amount,
            seller_last_online_date=seller_last_online_date,
            on_sell_number=on_sell_number
        )
        save_to_mysql(member)
        save_to_mysql(post)

        for i_name, i_path, i_url, i_relative_url in images:
            self.get_image(i_url, i_path, i_relative_url)
            page_source = page_source.replace(
                i_url,
                os.path.join(HTML_IMAGE_DIR, i_name)
            )
            if 'download/file.php' in i_url:
                page_source = page_source.replace(
                    '.' + i_relative_url,
                    os.path.join(HTML_IMAGE_DIR, i_name)
                )
            post_image = Image(
                post_id=post_id,
                path=i_path,
                url=i_relative_url
            )
            save_to_mysql(post_image)
        with codecs.open(os.path.join(BASE_DIR, HTML_DIR, '{}.html'.format(post_id)), 'w', 'utf-8') as f:
            f.write(page_source)

    def get_image(self, url, path, relative_url):
        path = os.path.join(BASE_DIR, path)
        self.driver_get(url, download=True)
        time.sleep(1)
        if len(self.driver.window_handles) > 1:
            self.driver.find_element_by_tag_name('img').screenshot(path)
            self.driver.close()
            self.driver.switch_to(self.driver.window_handles[0])
        else:
            try:
                shutil.move(
                    os.path.join(BASE_DIR, IMAGE_DIR, relative_url.strip('/')),
                    os.path.join(path)
                )
            except FileNotFoundError as _:
                self.driver.save_screenshot(path)
                self.driver.back()


def save_to_mysql(ob):
    conn = MySQLdb.connect(
        MYSQL_HOST,
        MYSQL_USER,
        MYSQL_PASSWORD,
        CHINESE_FORUM_MYSQL_DATABASE_NAME,
        charset='utf8mb4',
        use_unicode=True)
    cursor = conn.cursor()
    sql, params = ob.get_insert_sql()
    if sql:
        try:
            cursor.execute(sql, params)
            conn.commit()
        except MySQLdb.OperationalError as e:
            print(e)


def execute_mysql(sql, params):
    conn = MySQLdb.connect(
        MYSQL_HOST,
        MYSQL_USER,
        MYSQL_PASSWORD,
        CHINESE_FORUM_MYSQL_DATABASE_NAME,
        # 注意这里是utf8
        charset='utf8',
        use_unicode=True)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    return cursor


if __name__ == "__main__":
    # TODO 需要先运行TorProxy下面的run.bat
    master = MasterSpider()
    master.run_spider()
