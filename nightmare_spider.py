import time
from selenium.webdriver import Chrome, ChromeOptions, DesiredCapabilities
from django import setup
from datetime import datetime
import os
import re
import requests
from bs4 import BeautifulSoup

from django.core.exceptions import ObjectDoesNotExist
from TorProxy.tor_controller import restart_tor
from settings import HEADERS, IMAGE_HEADERS, BASE_DIR, NIGHTMARE_USERNAME, NIGHTMARE_PASSWORD, \
    NIGHTMARE_HTML_DIR, NIGHTMARE_HTML_IMAGE_DIR, NIGHTMARE_PIN
from utils import trans

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketWeb.settings')
setup()
from nightmare.models import Product, Category, VerifiedUser, FeedbackStatistics, SellerFeedback, \
    FeedbackLeftAsSeller, Seller, ProductImage, ProductFeedBack, SiteData, Buyer, Tag, ProductTag, Country, \
    ProductShipsFrom, ProductShipsTo


class Spider:
    start_url = 'http://nightmareocykhgs.onion'
    proxies = {'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'}
    dator = None
    LOGIN = False
    HEADERS = HEADERS
    IMAGE_HEADERS = IMAGE_HEADERS
    driver = None
    timeout_num = 0

    def __init__(self):
        desired_capabilities = DesiredCapabilities().CHROME
        desired_capabilities['pageLoadStrategy'] = 'none'
        options = ChromeOptions()
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
        self.driver = Chrome(options=options, desired_capabilities=desired_capabilities)

    def get_site_data(self, response):
        print('get site current data')
        html = BeautifulSoup(response.text, 'lxml')

        active_user_num, active_seller_num = re.search('Active users: (\d+) \| Active vendors: (\d+)', html.select(
            'body div.fixed-footer div div:nth-child(1) div div:nth-child(1)')[0].text.strip()).groups()
        currency = float(re.search(r'(\d+\.?\d*)', html.select(
            'body div.contentplace div div.row.topheader div:nth-child(1) div div.col-lg-5.bartop.pl-2 b')[
            0].text.strip()).groups()[0])
        SiteData(
            active_user_num=int(active_user_num),
            active_seller_num=int(active_seller_num),
            currency=currency,
            datetime=datetime.now().replace(second=0, microsecond=0)
        ).save()

    def login(self):
        if not self.LOGIN:
            print('try to login')

            self.driver_get('http://nightmareocykhgs.onion')
            start_time = time.time()
            while True:
                if 'ddos' not in self.driver.current_url:
                    break
                else:
                    if time.time() - start_time > 30:
                        start_time = time.time()
                        self.driver.refresh()
                    try:
                        self.driver.find_element_by_name(
                            'captcha_code').click()
                    except Exception as __:
                        pass

            self.driver_get('http://nightmareocykhgs.onion/login')
            start_time = time.time()
            while True:
                if 'login' not in self.driver.current_url:
                    break
                else:
                    if time.time() - start_time > 30:
                        start_time = time.time()
                        self.driver.refresh()
                    try:
                        username = self.driver.find_element_by_name(
                            'user')
                        if not username.get_attribute('value'):
                            username.send_keys(NIGHTMARE_USERNAME)
                        password = self.driver.find_element_by_name(
                            'pass')
                        if not password.get_attribute('value'):
                            password.send_keys(NIGHTMARE_PASSWORD)
                        code = self.driver.find_element_by_name('captcha_code')
                        code.click()
                    except Exception as __:
                        pass
            cookie = '{}={}'.format(self.driver.get_cookies()[0]['name'],
                                    self.driver.get_cookies()[0]['value'])
            self.HEADERS['Cookie'] = cookie
            self.IMAGE_HEADERS['Cookie'] = cookie
            self.LOGIN = True
            print('login success')
            if 'mnemonic' in self.driver.current_url:
                try:
                    self.driver.find_element_by_name('mnemonic').send_keys(self.driver.find_element_by_css_selector(
                        'body div.contentplace div:nth-child(9) div div div.offset-md-1.col-md-10 div.alert.alert-secondary center').text.strip().replace(
                        '"', ''))
                    self.driver.find_element_by_name('dat').click()
                except Exception as __:
                    pass

    def driver_get(self, url):
        if 'login' in url or url == 'http://nightmareocykhgs.onion':
            if self.LOGIN:
                return
        print('driver get ', url)
        self.driver.get(url)
        try:
            time.sleep(10)
            self.driver.find_element_by_css_selector('body')
        except Exception as __:
            restart_tor()
            time.sleep(10)
            self.driver_get(url)
            return

        if 'main-frame-error' in self.driver.page_source:
            restart_tor()
            self.LOGIN = False
            self.driver.close()
            desired_capabilities = DesiredCapabilities().CHROME
            desired_capabilities['pageLoadStrategy'] = 'none'
            options = ChromeOptions()
            options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
            self.driver = Chrome(options=options, desired_capabilities=desired_capabilities)
            if not self.LOGIN:
                self.login()
            self.driver_get(url)
            time.sleep(10)
            return

    def get_response(self, url, headers=None):
        print('get ', url)
        if not headers:
            headers = self.HEADERS
        try:
            response = requests.get(url=url, proxies=self.proxies, headers=headers, timeout=15)
            self.timeout_num = 0
        except Exception as e:
            print(e)
            restart_tor()
            self.timeout_num += 1
            if self.timeout_num > 10:
                self.login()
                self.timeout_num = 0
            return self.get_response(url)

        try:
            if 'http://nightmareocykhgs.onion/ddos/' in response.url:
                self.driver_get('http://nightmareocykhgs.onion/ddos')
                time.sleep(10)
                while True:
                    if 'ddos' not in self.driver.current_url:
                        break
                response = self.get_response(url)

            if response.status_code // 100 == 5:
                print(response.status_code)
                restart_tor()
                time.sleep(10)
                self.timeout_num += 1
                if self.timeout_num > 10:
                    self.login()
                    self.timeout_num = 0
                return self.get_response(url)
            location = response.headers.get('location', None)

            if location:
                self.HEADERS['Referer'] = url
                if 'http://' not in location:
                    location = self.start_url + response.headers['location']
                print('302 redirect to ', location)
                return self.get_response(location)
            self.update_dator(response)
        except AttributeError as __:
            restart_tor()
            time.sleep(10)
            self.timeout_num += 1
            return self.get_response(url)
        if response:
            return response
        else:
            self.timeout_num += 1
            return self.get_response(url)

    def get_post_response(self, url, data):
        print('post ', url)
        try:
            response = requests.post(proxies=self.proxies, url=url, data=data, headers=self.HEADERS, timeout=15)
        except Exception as e:
            print(e)
            restart_tor()
            self.timeout_num += 1
            if self.timeout_num > 10:
                self.login()
                self.timeout_num = 0
            return self.get_post_response(url, data)
        if 'http://nightmareocykhgs.onion/ddos/' in response.url:
            self.verify_captcha(response.url)
            response = self.get_post_response(url, data)
        location = response.headers.get('location', None)

        if location:
            if 'http://' not in location:
                location = self.start_url + response.headers['location']
            print('302 redirect to ', location)
            self.get_response(location)
        self.update_dator(response)
        return response

    def get_image_response(self, url, headers):
        print('get image ', url)
        return self.get_response(url, headers)

    def driver_save_image(self, url, args=''):
        print('driver save image', url)
        re_match = re.match(r'^.*?/(\d+)/(\d+)/(\d+)/(.*?)$', url)
        if re_match:
            image_name = '_'.join(re_match.groups())
        else:
            image_name = '_'.join(re.search(r'.*/(.*?)/(.*?\..*?)', url).groups())
        if args != '':
            image_name = args + '_' + image_name
        if '.jpg' not in image_name and '.png' not in image_name:
            image_name += '.png'
        relative_path = os.path.join(NIGHTMARE_HTML_IMAGE_DIR, image_name)
        self.driver.execute_script('window.open("{}");'.format(url))
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.save_screenshot(os.path.join(BASE_DIR, NIGHTMARE_HTML_DIR, relative_path))
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return relative_path

    def get_categories_list(self):
        print('get categories list')
        categories_list = []
        for i in self.driver.find_elements_by_css_selector(
                '#mySideBar div:nth-child(1) div.body ul a.nodecoration.bold'):
            c_url = i.get_attribute('href')
            c_name, product_num = re.match(r'^(.*?)(\d+)$', i.text).groups()
            categories_list.append([c_name.strip(), c_url, int(product_num.strip())])
        return categories_list

    def verify_captcha(self, referer):
        print('verify captcha')
        headers = self.IMAGE_HEADERS
        headers['Referer'] = referer
        response = self.get_image_response(self.start_url + '/captcha.php', headers)
        image = response.content
        with open('temp.png', 'wb') as img:
            img.write(image)

        captcha_code = input('please input captcha code:').strip()
        return captcha_code

    def update_dator(self, response):
        print('update dator')
        re_search = re.search(
            r'<input.*?name="dator".*?value="(.*?)"/>',
            response.content.decode('utf8', errors='ignore')
        )
        if re_search:
            self.dator = re_search.groups()[0]

    def parse_category_page(self):
        print('parse category page')
        # TODO for c_name, c_url, product_number in self.get_categories_list():
        for c_name, c_url, product_number in self.get_categories_list()[2:]:
            self.HEADERS['Referer'] = 'http://nightmareocykhgs.onion'
            response = self.get_response(c_url)
            html = BeautifulSoup(response.text, 'lxml')
            page_number = int(html.select('button.btn.btn-primary')[-2].text.strip())
            category = Category(name=c_name, page_number=page_number, url=c_url, product_number=product_number)
            category.save()
            for p in html.select('div.col-md-4.p-0'):
                product_url = p.select('h5 b a')[0]['href']
                seller_url = p.select('a')[2]['href']
                seller = self.parse_seller(seller_url)
                self.parse_product(product_url, seller, category)

            # TODO for p_num in range(2, page_number + 1):
            for p_num in range(2, 8):
                self.HEADERS['Referer'] = c_url
                response = self.get_post_response(c_url, data={
                    'title': '',
                    'search': '1',
                    'searchcat': '1',
                    'type': 'all',
                    'payment': 'all',
                    'priceMin': '',
                    'priceMax': '',
                    'shipsfrom': 'all',
                    'shipsto': 'all',
                    'field': 'all',
                    'order': 'all',
                    'displayname': '',
                    'dator': self.dator,
                    'cat': c_url[-4:],
                    'page': str(p_num),
                })
                html = BeautifulSoup(response.text, 'lxml')
                for p in html.select('div.col-md-4.p-0'):
                    product_url = p.select('h5 b a')[0]['href']
                    seller_url = p.select('div.col-md-12 a.green')[0]['href']
                    self.HEADERS['Referer'] = c_url
                    seller = self.parse_seller(seller_url)
                    self.HEADERS['Referer'] = c_url
                    product = self.parse_product(product_url, seller, category)

    def parse_seller(self, url):
        print('parse seller')
        try:
            seller = Seller.objects.get(url=url)
        except ObjectDoesNotExist:
            pass
        else:
            return seller
        response = self.get_response(url)
        html = BeautifulSoup(response.text, 'lxml')
        re_search = re.findall(
            r'([\s\w]*?):.*?\(([\d,]+)\).*?\((\d+\.?\d*)\)',
            html.select(
                '#mainContent div div.row.profileside div.col-md-7 p:nth-child(9)')[0].text.replace('Verified user:',
                                                                                                    '').strip()
        )
        verified_user = None
        if re_search:
            for v_name, v_sales, v_rating in re_search:
                verified_user = VerifiedUser(
                    name=v_name.strip(),
                    sales=int(v_sales.replace(',', '')),
                    rating=float(v_rating)
                )
            verified_user.save()
        try:
            seller = Seller.objects.get(url=url)
            seller.verified_user = verified_user
        except ObjectDoesNotExist:
            pass
        else:
            return seller
        name, order_num, rating, trust_level, live_jabber_notification, level, followers_num, member_since = re.search(
            r'(.+) (\d+).*?([1-5]+\.?\d*).*?Trust Level (\d+).*?Live jabber notification:.*?([InAactive]+).*?Level: (.*) - Followers.*?(\d+).*?Member since: (.*)',
            html.select(
                '#mainContent div div.row.profileside div.col-md-7')[0].text, re.S).groups()
        name = name.strip()
        image_url = html.select(
            '#mainContent div div.row.profileside div.col-md-2 img')[0]['src']
        image_path = self.parse_seller_image(url, image_url, name)
        html_path = self.save_html(response, 'seller', [(image_url, image_path)])
        tmp_html = html.select('#tabs table tbody tr')
        order_num = int(order_num)
        rating = float(rating)
        trust_level = int(trust_level)
        live_jabber_notification = 'In' not in live_jabber_notification
        followers_num = int(followers_num)
        member_since = datetime.strptime(member_since.strip(), '%B %d, %Y').date()
        one_month_positive_feedback_num, six_month_positive_feedback_num, since_join_positive_feedback_num = \
            html.select(
                '#mainContent table tbody tr:nth-child(1)')[0].text.strip().split('\n')[1:]
        one_month_negative_feedback_num, six_month_negative_feedback_num, since_join_negative_feedback_num = \
            html.select(
                '#mainContent table tbody tr:nth-child(2)')[0].text.strip().split(
                '\n')[1:]
        feedback_statistics = FeedbackStatistics(
            one_month_positive_feedback_num=int(one_month_positive_feedback_num),
            six_month_positive_feedback_num=int(six_month_positive_feedback_num),
            since_join_positive_feedback_num=int(since_join_positive_feedback_num),
            one_month_negative_feedback_num=int(one_month_negative_feedback_num),
            six_month_negative_feedback_num=int(six_month_negative_feedback_num),
            since_join_negative_feedback_num=int(since_join_negative_feedback_num),
        )
        feedback_statistics.save()

        about = self.parse_seller_about(url)
        pgp = self.parse_seller_pgp(url)
        news = self.parse_seller_news(url)
        icq, jabber = self.parse_seller_contact(url)
        seller = Seller(
            url=url,
            name=name,
            order_num=order_num,
            rating=rating,
            trust_level=trust_level,
            verified_user=verified_user,
            live_jabber_notification=live_jabber_notification,
            level=level,
            followers_num=followers_num,
            member_since=member_since,
            feedback_statistics=feedback_statistics,
            about=about,
            chinese_about=trans(about),
            pgp=pgp,
            news=news,
            icq=icq,
            jabber=jabber,
            image_url=image_url,
            image_path=image_path,
            html_path=html_path
        )
        seller.save()
        try:
            for tr in tmp_html:
                if tr and tr != '\n':
                    try:
                        td_list = tr.select('td')
                    except Exception as e:
                        print(e)
                    else:
                        negative_or_positive = 'fa-plus-square' in td_list[0].__str__()
                        product_url = td_list[1].select('a')[0]['href']
                        content = td_list[1].text.strip()
                        buyer = Buyer(td_list[2].text.split(' ')[0].strip().replace('USD', ''))
                        buyer.save()
                        price = float(td_list[2].select('span')[0].text.replace('USD ', '').strip())
                        try:
                            _datetime = datetime.strptime(td_list[3].select('span')[0].text.strip(),
                                                          '%B %d,%Y %H:%M')
                        except ValueError as e:
                            print(e)
                            _datetime = datetime(1900, 1, 1)
                        rating = len(td_list[4].select('i.fa.fa-star'))
                        SellerFeedback(
                            seller=seller,
                            negative_or_positive=negative_or_positive,
                            content=content,
                            buyer=buyer,
                            price=price,
                            datetime=_datetime,
                            rating=rating,
                            product_url=product_url
                        ).save()
        except IndexError as __:
            pass
        response = self.get_response(url.replace('feedbackreceived', 'feedbackleft'))
        for tr in BeautifulSoup(response.text, 'lxml').select('#tabs table tbody tr'):
            td_list = tr.select('td')
            negative_or_positive = 'green' in td_list[0].__str__()
            buyer = Buyer(td_list[2].text.strip().split(' ')[0].replace('USD', ''))
            buyer.save()
            content = td_list[1].text.strip()
            price = float(td_list[2].select('span')[0].text.replace('USD ', '').strip())
            _datetime = datetime.strptime(td_list[3].select('span')[0].text.strip(), '%B %d,%Y %H:%M')
            rating = len(td_list[4].select('i.fa.fa-star'))
            FeedbackLeftAsSeller(
                negative_or_positive=negative_or_positive,
                content=content,
                seller=seller,
                buyer=buyer,
                price=price,
                datetime=_datetime,
                rating=rating,
            ).save()
        return seller

    def parse_seller_image(self, url, image_url, name):
        headers = self.IMAGE_HEADERS
        headers['Referer'] = url
        return self.save_image(image_url, args=name, headers=headers)

    def parse_seller_about(self, url):
        self.HEADERS['Referer'] = url
        response = self.get_response(url.replace('feedbackreceived', 'about'))
        return BeautifulSoup(response.text, 'lxml').select('#tabs')[0].text.strip()

    def parse_seller_pgp(self, url):
        self.HEADERS['Referer'] = url
        response = self.get_response(url.replace('feedbackreceived', 'pgp'))
        return BeautifulSoup(response.text, 'lxml').select('#tabs')[0].text.strip()

    def parse_seller_news(self, url):
        self.HEADERS['Referer'] = url
        response = self.get_response(url.replace('feedbackreceived', 'news'))
        return BeautifulSoup(response.text, 'lxml').select('#tabs')[0].text.strip()

    def parse_seller_contact(self, url):
        self.HEADERS['Referer'] = url
        response = self.get_response(url.replace('feedbackreceived', 'contact'))
        icq = re.search(r'ICQ :(.*?)<br', response.text).groups()[0].strip()
        jabber = re.search(r'Jabber :(.*?)<br', response.text).groups()[0].strip()
        return icq, jabber

    def parse_product(self, url, seller, category):
        print('parse product')

        try:
            product = Product.objects.get(url=url)
        except ObjectDoesNotExist:
            pass
        else:
            return product
        response = self.get_response(url)
        html = BeautifulSoup(response.text, 'lxml')
        tmp_html = html.select(
            '#listingsPlace div:nth-child(3) div.col-md-4.listingimages a')
        images_url_path_list = self.parse_product_image(url, tmp_html, url)
        html_path = self.save_html(response, 'product', images_url_path_list)
        title = html.select('#listingsPlace div.col-md-9 h4')[0].text.strip()
        tbody = html.select('#listingsPlace div:nth-child(3) div.col-md-8 table tbody')[0]
        quantity_left = 0
        view_num = 0
        payment = ''
        visibility = ''
        ships_from = ''
        ships_to = ''
        ends_in = ''
        for i, iv in enumerate(tbody.select('td')[::2]):
            value = tbody.select('td')[1::2][i].text.strip()
            if 'Quantity' in iv.text:
                if 'Unlimited' in value:
                    quantity_left = 99999
                else:
                    quantity_left = int(value)
            elif 'Views' in iv.text:
                view_num = int(value)
            elif 'Payment' in iv.text:
                payment = value
            elif 'Visibility' in iv.text:
                visibility = value
            elif 'from' in iv.text:
                ships_from = value
            elif 'to' in iv.text:
                ships_to = value
            elif 'Ends' in iv.text:
                ends_in = value

        description = html.select('#listingsPlace div.tabsbody p')[0].text.strip()
        price = float(re.search(r'Total Purchase Price : USD (\d+\.?\d*)',
                                html.select(
                                    '#listingsPlace div:nth-child(3) div.col-md-8 h4')[0].text
                                ).groups()[0])
        tags_html = html.select('#listingsPlace div.tabsbody nav ul li')
        refund_policy = self.parse_product_refund_policy(url)
        terms_conditions = self.parse_product_terms_conditions(url)
        product = Product(
            title=title,
            chinese_title=trans(title),
            url=url,
            seller=seller,
            category=category,
            quantity_left=quantity_left,
            view_num=view_num,
            payment=payment,
            visibility=visibility,
            price=price,
            description=description,
            chinese_description=trans(description),
            refund_policy=refund_policy,
            terms_conditions=terms_conditions,
            ends_in=ends_in,
            html_path=html_path
        )
        product.save()

        for i in tags_html:
            for t in i.text.strip().split(' '):
                t = t.replace('#', '').replace('(', '').replace(')', '').replace('\n', ' ').replace('/',
                                                                                                    ' ').lower().strip()
                if t and t != '/' and len(t) > 1:
                    try:
                        tag = Tag.objects.get(name=t)
                    except Exception as _:
                        tag = Tag(name=t, number=0)
                    tag.number += 1
                    tag.save()
                    ProductTag(tag=tag, product=product).save()
        for i in ships_from.split(','):
            name = i.strip()
            if name != '':
                if name == 'USA & Canada':
                    try:
                        tmp_country_1 = Country.objects.get(name='United States')
                    except Exception as _:
                        tmp_country_1 = Country(name='United States')
                    try:
                        tmp_country_2 = Country.objects.get(name='Canada')
                    except Exception as _:
                        tmp_country_2 = Country(name='Canada')
                    tmp_country_1.from_number += 1
                    tmp_country_2.from_number += 1
                    tmp_country_1.save()
                    tmp_country_2.save()
                    ProductShipsFrom(country=tmp_country_1, product=product).save()
                    ProductShipsFrom(country=tmp_country_2, product=product).save()
                else:
                    try:
                        country = Country.objects.get(name=name)
                    except Exception as _:
                        country = Country(name=name)
                    country.from_number += 1
                    country.save()
                    ProductShipsFrom(country=country, product=product).save()
        for i in ships_to.split(','):
            name = i.strip()
            if name != '':
                if name == 'USA & Canada':
                    try:
                        tmp_country_1 = Country.objects.get(name='United States')
                    except Exception as _:
                        tmp_country_1 = Country(name='United States')
                    try:
                        tmp_country_2 = Country.objects.get(name='Canada')
                    except Exception as _:
                        tmp_country_2 = Country(name='Canada')
                    tmp_country_1.to_number += 1
                    tmp_country_2.to_number += 1
                    tmp_country_1.save()
                    tmp_country_2.save()
                    ProductShipsTo(country=tmp_country_1, product=product).save()
                    ProductShipsTo(country=tmp_country_2, product=product).save()
                else:
                    try:
                        country = Country.objects.get(name=name)
                    except Exception as _:
                        country = Country(name=name)
                    country.to_number += 1
                    country.save()
                    ProductShipsTo(country=country, product=product).save()
        self.parse_product_feedback(url, product, seller)

        if datetime.now().minute % 10 == 0:
            self.get_site_data(response)
        return product

    def parse_product_refund_policy(self, url):
        self.HEADERS['Referer'] = url
        response = self.get_response(url.replace('description', 'refundpolicy'))
        html = BeautifulSoup(response.text, 'lxml')
        return html.select('#listingsPlace div.tabsbody p')[0].text.strip()

    def parse_product_terms_conditions(self, url):
        self.HEADERS['Referer'] = url
        response = self.get_response(url.replace('description', 'termsandconditions'))
        html = BeautifulSoup(response.text, 'lxml')
        return html.select('#listingsPlace div.tabsbody p')[0].text.strip()

    def parse_product_image(self, url, tmp_html, product_url):
        images_url_path_list = []
        headers = self.IMAGE_HEADERS
        headers['Referer'] = url
        for i in tmp_html:
            href = i['href']
            if '#' != href:
                path = self.save_image(href, headers)
                images_url_path_list.append((href, path))
                ProductImage(url=href, path=path, product_url=product_url).save()
        return images_url_path_list

    def parse_product_feedback(self, url, product, seller):
        response = self.get_response(url.replace('description', 'feedbacks'))
        for tr in BeautifulSoup(response.text, 'lxml').select('#listingsPlace div.tabsbody table tbody tr'):
            # This product doesn\'t currently have any feedback.
            if 'currently have any feedback.' in tr.text:
                break
            td_list = tr.select('td')
            negative_or_positive = 'green' in td_list[0].__str__()
            content = td_list[1].text.strip()
            buyer = Buyer(td_list[2].text.strip().split('USD')[0])
            buyer.save()
            price = float(td_list[2].select('span')[0].text.replace('USD ', '').strip())
            try:
                _datetime = datetime.strptime(td_list[3].select('span')[0].text.strip(), '%B %d,%Y %H:%M')
            except Exception as __:
                _datetime = datetime.strptime(td_list[3].select('span')[0].text.strip(), '%B %d,%Y')
            rating = len(td_list[4].select('i.fa.fa-star'))
            ProductFeedBack(
                negative_or_positive=negative_or_positive,
                content=content,
                seller=seller,
                buyer=buyer,
                price=price,
                datetime=_datetime,
                rating=rating,
                product=product
            ).save()

    def save_image(self, url, headers, args=''):
        print('save image', url)

        re_match = re.match(r'^.*?/(\d+)/(\d+)/(\d+)/(.*?)$', url)
        if re_match:
            image_name = '_'.join(re_match.groups())
        else:
            image_name = '_'.join(re.search(r'.*/(.*?)/(.*?\..*?)', url).groups())
        if args != '':
            image_name = args + '_' + image_name
        if '.jpg' not in image_name and '.png' not in image_name:
            image_name += '.png'
        relative_path = os.path.join(NIGHTMARE_HTML_IMAGE_DIR, image_name)
        real_path = os.path.join(BASE_DIR, NIGHTMARE_HTML_DIR, relative_path)
        if os.path.exists(real_path):
            return relative_path
        with open(real_path, 'wb') as f:
            f.write(self.get_image_response(url, headers).content)
        return relative_path

    def run_spider(self):
        print('run spider')
        self.login()
        self.parse_category_page()

    def save_html(self, response, args='', images_url_path_list=None):
        if images_url_path_list is None:
            images_url_path_list = []
        html_name = '_'.join(response.url.split('/')[-3:]) + '.html'
        if args != '':
            html_name = args + '_' + html_name
        relative_path = os.path.join(NIGHTMARE_HTML_DIR, html_name)
        real_path = os.path.join(BASE_DIR, relative_path)
        if os.path.exists(real_path):
            return relative_path
        content = response.text
        if images_url_path_list:
            for url, path in images_url_path_list:
                content = content.replace(url, path)
        content = content.replace(
            'http://nightmareocykhgs.onion/files/',
            'css/')

        with open(real_path, 'wb') as f:
            f.write(content.encode('utf8'))
        return relative_path


if __name__ == '__main__':
    # TODO 需要先运行TorProxy下面的run.bat
    s = Spider()
    s.run_spider()
