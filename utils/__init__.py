import hashlib
import random
import urllib

import requests
import json

from marketWeb.settings import BAIDU_APPID, BAIDU_SECRETKEY


def get_attr(cls):
    return [i for i in cls.__dict__.keys() if not callable(getattr(cls, i)) and i[:2] != '__']


def trans(words, trans_from='en', trans_to='zh'):
    if words.isalpha() and trans_to == 'en':
        return words
    elif (not words.isalpha) and trans_to == 'zh':
        return words
    httpClient = None
    myurl = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    result = ''
    fromLang = trans_from
    toLang = trans_to
    salt = random.randint(32768, 65536)
    sign = BAIDU_APPID + words + str(salt) + BAIDU_SECRETKEY
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + BAIDU_APPID + '&q=' + urllib.parse.quote(
        words) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

    try:

        response = requests.get(myurl)
        js = json.loads(response.content)
        for i in js['trans_result']:
            result += i['dst'] + '\n'
    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()
        return result.strip()
