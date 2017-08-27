# -*- coding: UTF-8 -*-
# 建立索引excel
import re
import json
import time
import requests
import xlwings as xw
# 以下为自己编写的库文件
import enviroment
times = 1


def pass_502(url):
    global times
    print url
    response = requests.get(url=url, headers=enviroment.headers())
    bad_gateway = 1
    while re.search('502 Bad Gateway', response.content) is not None:
        time.sleep(0.2)
        bad_gateway += 1
        response = requests.get(url=url, headers=enviroment.headers())
    print 'bad gateway for ' + str(bad_gateway), times
    times += 1
    return response


def get_index(results, value_list):
    sheet = value_list[0]
    row = value_list[1]
    day = sheet.range('C'+str(row)).value
    mon = sheet.range('B'+str(row)).value
    if time.localtime(results[len(results)-1]['created_at']).tm_mday != day\
            or time.localtime(results[len(results)-1]['created_at']).tm_mon != mon:
        for i in range(0, len(results)):
            photo = results[i]
            if time.localtime(photo['created_at']).tm_mday != day\
                    or time.localtime(photo['created_at']).tm_mon != mon:
                row += 1
                s_time = time.mktime([time.localtime(photo['created_at']).tm_year,
                                      time.localtime(photo['created_at']).tm_mon,
                                      time.localtime(photo['created_at']).tm_mday,
                                      0, 0, 0, 0, 0, 0])
                sheet.range('A'+str(row)).value =\
                    [time.localtime(photo['created_at']).tm_year, time.localtime(photo['created_at']).tm_mon,
                     time.localtime(photo['created_at']).tm_mday, photo['id'], s_time / 100]
                day = sheet.range('C'+str(row)).value
                mon = sheet.range('B'+str(row)).value
                if time.localtime(results[len(results) - 1]['created_at']).tm_mday == day\
                        and time.localtime(results[len(results) - 1]['created_at']).tm_mon == mon:
                    break
    return [sheet, row]


def get_json(url, value_list):
    response = pass_502(url)
    value_list = get_index(response.json()['data']['results'], value_list)
    while 'next' in response.json()['data']:
        time.sleep(0.1)
        url = 'https://v2.same.com' + response.json()['data']['next']
        response = pass_502(url)
        value_list = get_index(response.json()['data']['results'], value_list)
    get_index(response.json()['data']['results'], value_list)


def index(sheet_name):
    with open(enviroment.info) as i:
        megs = json.loads(i.read())
    i.close()
    ids = megs['ids']
    urls = megs['urls']

    app = xw.App(visible=True, add_book=False)
    wb = app.books.open(enviroment.index)
    wb.sheets.add(sheet_name)
    row = 1

    sheet = wb.sheets[sheet_name]
    value_list = [sheet, row]
    print 'please wait...'
    get_json(urls[ids[sheet_name.decode('GBK')]], value_list)
    wb.sheets[sheet_name].range('A1').api.EntireRow.Delete()
    wb.sheets[sheet_name].range('A1').api.EntireRow.Delete()
    print sheet_name + 'index completed'
