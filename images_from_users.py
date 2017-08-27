# -*- coding: UTF-8 -*-
# 用于完整下载某用户所有图片
import os
import re
import time
import random
import requests
import argparse


def gen_id(length):
    chars = ['a', 'b', 'c', 'd', 'e', 'f', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    array = ''
    while length is not 0:
        array += random.choice(chars)
        length -= 1
    return array


def unionid():
    return (gen_id(8)+'-'+gen_id(4)+'-'+gen_id(4)+'-'+gen_id(4)+'-'+gen_id(12)).lower()


def mkdir(path):
    is_exists = os.path.exists(path)
    if not is_exists:
        print 'buid path = ' + path
        os.makedirs(path)


def get_image(image_url, user_id):
    global a
    r = requests.get(image_url)
    mkdir(img_name)
    img_dir = img_name + '\\' + str(user_id) + '.jpg'
    with open(img_dir, 'wb') as f:
        f.write(r.content)
    print '第' + str(a) + '张图片'
    a += 1


def to_image_url():
    global response, a
    results = response.json()['data']['results']
    for i in range(0, len(results)):
        if re.search('jpg', results[i]['photo']) is not None:
            get_image(results[i]['photo'],
                      results[i]['id'])


def get_url(the_url):
    global response, a
    header = {
        'X-Same-Request-ID': unionid(),
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
    session = requests.session()
    response = session.get(url=the_url, headers=header)
    bad_gateway = 0
    while re.search('502 Bad Gateway', response.content) is not None:
        time.sleep(0.1)
        bad_gateway += 1
        response = requests.get(url=the_url, headers=header)
    print 'bad gateway for ' + str(bad_gateway)
    to_image_url()
    while 'next' in response.json()['data']:
        nexturl = 'https://v2.same.com' + response.json()['data']['next']
        response = session.get(url=nexturl, headers=header)
        bad_gateway = 0
        while re.search('502 Bad Gateway', response.content) is not None:
            time.sleep(0.1)
            bad_gateway += 1
            response = requests.get(url=the_url, headers=header)
        print 'bad gateway for ' + str(bad_gateway)
        to_image_url()
    results = response.json()['data']['results']
    for i in range(0, len(results)):
        if re.search('jpg', results[i]['photo']) is not None:
            get_image(results[i]['photo'],
                      results[i]['id'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=u'下载某用户发布过的所有图片'.encode('GBK'))
    parser.add_argument('-u', nargs='?',
                        help=u'指向该用户的url中的数字'.encode('GBK'))
    parser.add_argument('-i', nargs='?',
                        help=u'用户名'.encode('GBK'))
    args = parser.parse_args()

    url = 'https://v2.same.com/user//' + args.u + '/senses'
    img_name = 'C:\\Users\\root\Pictures\Saved Pictures\same\\users\\' + args.i + '\\'

    a = 1
    response = ''
    get_url(url)
