# -*- coding: UTF-8 -*-
import random
info = r'info.json'
index = r'index.xlsx'


def headers():

    def union_id():

        def gen_id(length):
            chars = ['a', 'b', 'c', 'd', 'e', 'f', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
            array = ''
            while length is not 0:
                array += random.choice(chars)
                length -= 1
            return array

        ids = [gen_id(8), gen_id(4), gen_id(4), gen_id(4), gen_id(12)]
        return '-'.join(ids).lower()

    header = {
        'X-Same-Request-ID': union_id(),
        'X-same-Client-Version': '593',
        'Machine': 'android|301|android6.0.1|Redmi 3S|d:863316375146|720|1280',
        'Host': 'im-xs.same.com',
        'X-same-Device-UUID': 'd:863316375146',
        'PACKAGE-NAME': 'com.same.android',
        'User-Agent': 'same/593',
        'Connection': 'keep-alive',
        'Advertising-UUID': 'd:863316375146',
        'timezone': 'Asia/Shanghai',
        'Authorization': 'Token 1500806062-PZ12MW6jmh8W1nn2-15974677',
        'Extrainfo': 'yingyongbao',
        'Accept-Encoding': 'gzip'
    }
    return header
