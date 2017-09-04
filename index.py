# -*- coding: UTF-8 -*-
# 建立索引excel
"""
2017.9.4
将索引更新程序加入该程序，并改名为index（原名为“build_index”）
"""
import re
import json
import time
import requests
import xlwings as xw
# 以下为自己编写的库文件
import enviroment
times = 1


def update_what(channels):
    app = xw.App(visible=True, add_book=False)
    wb = app.books.open(enviroment.index)

    with open(enviroment.info) as i:
        megs = json.loads(i.read())
    ids = megs['ids']
    urls = megs['urls']
    names = megs['names']
    i.close()

    if channels == 'all':
        for name in names:
            update_index(urls[ids[name]], wb.sheets[name.encode('GBK')])
    else:
        update_index(urls[ids[channels]], wb.sheets[channels])

    wb.save()
    app.quit()


def update_index(url, sheet):
    excel_list = []
    finish = 1  # 循环结束标志
    response = pass_502(url)
    results = response.json()['data']['results']
    # 保存这次更新中最新写入的时间
    t = time.localtime(results[0]['created_at'])
    year = t.tm_year
    mon = t.tm_mon
    day = t.tm_mday
    # 以下三个时间是之前索引的最近年、月、日，是比较的对象
    last_year = sheet.range('A1').value
    last_mon = sheet.range('B1').value
    last_day = sheet.range('C1').value
    if year != last_year or mon != last_mon or day != last_day:
        t_list = [year, mon, day, 0, 0, 0, 0, 0, 0]  # 用于使用生成以秒计时间
        excel_list.append([year, mon, day, results[0]['id'], time.mktime(t_list) / 100])
        sheet.range('A1').api.EntireRow.Insert()
    while finish:
        for text in results:
            if year == last_year and mon == last_mon and day == last_day:
                finish = 0
                break
            else:
                # t的时间为当前数据包中循环到的图片的时间
                t = time.localtime(text['created_at'])
                if year != t.tm_year or mon != t.tm_mon or day != t.tm_mday:
                    year = t.tm_year
                    mon = t.tm_mon
                    day = t.tm_mday
                    t_list = [year, mon, day, 0, 0, 0, 0, 0, 0]  # 用于使用生成以秒计时间
                    excel_list.append([year, mon, day, text['id'], time.mktime(t_list) / 100])
                    sheet.range('A1').api.EntireRow.Insert()
        if finish:
            next_url = 'https://v2.same.com' + response.json()['data']['next']
            response = pass_502(next_url)
            results = response.json()['data']['results']
    if excel_list is None:
        print 'no image to update'
    else:
        # 如果更新当日没有新的图片，则不删除
        if excel_list[0][2] == time.localtime(time.time()).tm_mday:
            excel_list.pop(0)
            sheet.range('A1').api.EntireRow.Delete()
        if excel_list:
            for x in range(0, len(excel_list)):
                sheet.range('A'+str(x+1)).value = excel_list[x]
                print 'update index : ', excel_list[x]


def build_index(sheet_name):
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


def get_json(url, value_list):
    response = pass_502(url)
    value_list = get_index(response.json()['data']['results'], value_list)
    while 'next' in response.json()['data']:
        time.sleep(0.1)
        url = 'https://v2.same.com' + response.json()['data']['next']
        response = pass_502(url)
        value_list = get_index(response.json()['data']['results'], value_list)
    get_index(response.json()['data']['results'], value_list)


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


def pass_502(url):
    global times
    response = requests.get(url=url, headers=enviroment.headers())
    bad_gateway = 1
    while re.search('502 Bad Gateway', response.content) is not None:
        time.sleep(0.2)
        bad_gateway += 1
        response = requests.get(url=url, headers=enviroment.headers())
    print 'bad gateway for ' + str(bad_gateway), times
    times += 1
    return response
