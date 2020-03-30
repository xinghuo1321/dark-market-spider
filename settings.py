# -*- coding: utf-8 -*-
# 爬虫配置信息
import os

BASE_DIR = os.getcwd()

MYSQL_HOST = ''
CHINESE_FORUM_MYSQL_DATABASE_NAME = ''
MYSQL_USER = ''
MYSQL_PASSWORD = ''

HTML_DIR = 'templates'
HTML_IMAGE_DIR = 'images'
IMAGE_DIR = os.path.join(HTML_DIR, HTML_IMAGE_DIR)
USERNAME = ''
PASSWORD = ''

NIGHTMARE_HTML_DIR = os.path.join('templates', 'nightmare')
NIGHTMARE_HTML_IMAGE_DIR = 'images'
NIGHTMARE_USERNAME = ''
NIGHTMARE_PASSWORD = ''
NIGHTMARE_PIN = ''
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'deflate',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'DNT': '1',
    'Host': 'nightmareocykhgs.onion',
    'Origin': 'http://nightmareocykhgs.onion',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}

IMAGE_HEADERS = {
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': 'nightmareocykhgs.onion',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}
