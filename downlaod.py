# -*- coding: UTF-8 -*-
# 使用info.json中的信息下载图片
"""
2017.9.1
修改频道索引更新程序：
1.若程序更新当日没有图片，则更新程序会删除原本应被记录的索引
  如8.3下载8.1-8.2的图片，但8.3没有图片，则更新后只有8.1的图片，没有8.2的图片
修改图片下载程序

2017.9.4
修改图片下载程序：
下载的图片要求发布者必须为女性
"""
import os
import re
import time
import json
import requests
import xlwings as xw
import enviroment
num_of_image = 0


def download(c, t, p):
    value_dict = {}

    with open(enviroment.info) as i:
        megs = json.loads(i.read())
    ids = megs['ids']
    urls = megs['urls']
    paths = megs['paths']
    names = megs['names']
    i.close()

    channels = []
    if c:
        for i in c:
            channels.append(i.decode('GBK'))
    time_list = get_date_zone(t)
    files = {}
    if p:
        for i in range(0, len(p), 2):
            files[ids[p[i].decode('GBK')]] = p[i+1].decode('GBK')

    app = xw.App(visible=True, add_book=False)
    wb = app.books.open(enviroment.index)
    start_time = time.asctime(time.localtime(time.time()))
    if channels:
        for channel in channels:
            print channel.encode('GBK')
            global_id = ids.get(channel)
            the_channel = channel.encode('GBK')
            if global_id in files:
                path = files.get(global_id)
            else:
                path = paths.get(global_id)
            value_dict['t'] = t
            value_dict['path'] = path
            value_dict['channel'] = the_channel
            download_from_index(urls.get(global_id), wb.sheets[channel.encode('GBK')], time_list, value_dict)
    else:
        for channel in names:
            print channel.encode('GBK')
            global_id = ids.get(channel)
            the_channel = channel.encode('GBK')
            if global_id in files:
                path = files.get(global_id)
            else:
                path = paths.get(global_id)
            value_dict['t'] = t
            value_dict['path'] = path
            value_dict['channel'] = the_channel
            download_from_index(urls.get(global_id), wb.sheets[channel.encode('GBK')], time_list, value_dict)
    print start_time, '\n', time.asctime(time.localtime(time.time()))

    wb.save()
    app.quit()


def update_index(url, sheet):
    excel_list = []
    finish = 1  # 标记是否更新到之前索引的最近一天
    response = pass_502(url)
    results = response.json()['data']['results']
    year = mon = day = 1  # 保存这次更新中最新写入的时间
    # 以下三个时间是之前索引的最近年、月、日，是比较的对象
    last_year = sheet.range('A1').value
    last_mon = sheet.range('B1').value
    last_day = sheet.range('C1').value
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
    excel_list.pop()
    sheet.range('A1').api.EntireRow.Delete()
    # 如果更新当日没有新的图片，则不删除
    if excel_list[0][2] == time.localtime(time.time()).tm_mday:
        excel_list.pop(0)
        sheet.range('A1').api.EntireRow.Delete()
    # 由于时间比较在新建单元格和写入list前，因此跳出循环时excel_list必然多一项重复的上次更新的最新时间，将其删除
    for x in range(0, len(excel_list)):  # 第一个必然是今日的数据，但今日的不写入excel
        sheet.range('A'+str(x+1)).value = excel_list[x]
        print 'update index : ', excel_list[x]


def download_from_index(the_url, sheets, time_list, value_dict):
    total_list = sheets.range('D1:E1500').value
    start = 0
    for x in range(len(total_list)):
        if total_list[x][0] is None:
            print 'there is no image'
            return 0
        elif time_list[0] / 100 <= total_list[x][1] <= time_list[1] / 100:
                start = total_list[x][0]
                break
    the_url = the_url + '?offset=' + str(int(start))

    response = pass_502(the_url)
    mark = get_url(response.json()['data']['results'], time_list, value_dict)
    while mark:
        next_url = 'https://v2.same.com' + response.json()['data']['next']
        response = pass_502(next_url)
        mark = get_url(response.json()['data']['results'], time_list, value_dict)


def get_url(results, time_list, value_dict):
    stop = 1
    for photo in results:
        if time_list[0] <= int(photo['created_at']) <= time_list[1] and re.search('jpg', photo['photo']) is not None \
                and photo['user']['sex'] == 2:
            get_image(photo['photo'], str(photo['id']), str(photo['user_id']), value_dict)
        elif int(photo['created_at']) < time_list[0]:
            stop = 0
            return stop
    return stop


def get_image(image_url, image_id, user_id, value_dict):
    global num_of_image
    path = value_dict['path']
    channel = value_dict['channel']
    t = value_dict['t']
    r = requests.get(image_url)

    img_name = path
    img_dir = img_name + '\\' + image_id + 'same' + user_id + '.jpg'  # “same”使得以大图标查看时，用户名都在第二行
    with open(img_dir, 'wb') as f:
        f.write(r.content)

    if len(t) == 1:
        img_name = enviroment.path + t[0] + '\\' + channel
    else:
        img_name = enviroment.path + t[0] + '-' + t[1] + '\\' + channel
    is_exists = os.path.exists(img_name)
    if not is_exists:
        print 'build path = ' + img_name
        os.makedirs(img_name)
    img_dir = img_name + '\\' + image_id + 'same' + user_id + '.jpg'  # “same”使得以大图标查看时，用户名都在第二行
    with open(img_dir, 'wb') as f:
        f.write(r.content)

    num_of_image += 1
    print channel + ' ' + str(image_id) + ' : ' + 'image ' + str(num_of_image)


def pass_502(url):
    response = requests.get(url=url, headers=enviroment.headers())
    bad_gateway = 1
    while re.search('502 Bad Gateway', response.content) is not None:
        time.sleep(0.2)
        bad_gateway += 1
        response = requests.get(url=url, headers=enviroment.headers())
    print 'bad gateway for ' + str(bad_gateway)
    return response


def change_time():
    # 以“年.月.日”格式返回当前日期前一周的时间
    now = time.localtime(time.time())
    now_day = [now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0, 0, 0, 0]
    first_day = time.mktime(now_day) - 7 * 86400
    last_day = time.mktime(now_day) - 86400
    now = time.localtime(first_day)
    weekday1 = str(now.tm_year) + '.' + str(now.tm_mon) + '.' + str(now.tm_mday)
    now = time.localtime(last_day)
    weekday2 = str(now.tm_year) + '.' + str(now.tm_mon) + '.' + str(now.tm_mday)
    return [weekday1, weekday2]


def get_date_zone(date):
    date_list = date[0].split('.')
    for x in range(3):
        date_list[x] = int(date_list[x])
    for x in range(6):
        date_list.append(0)
    date_from = time.mktime(date_list)
    if len(date) == 1:
        date_list[3] = 24
        date_to = time.mktime(date_list)
    else:
        date_list = date[1].split('.')
        for x in range(3):
            date_list[x] = int(date_list[x])
        for x in range(6):
            date_list.append(0)
        date_list[3] = 24
        date_to = time.mktime(date_list)
    return date_from, date_to
