# -*- coding: UTF-8 -*-
# 用于增加、更新和删除频道信息
import json
import enviroment


def add(new_info, default):
    channel_name = new_info[0].decode('GBK')
    channel_id = new_info[1]
    channel_path = new_info[2].decode('GBK')
    with open(enviroment.info) as f:
        info = json.loads(f.read())
    f.close()
    info['ids'][channel_name] = channel_id
    info['urls'][channel_id] = 'https://v2.same.com/channel/' + channel_id + '/senses'
    info['paths'][channel_id] = channel_path
    if default:
        info['names'].append(channel_name)
    with open(enviroment.info, 'w') as f:
        f.write(json.dumps(info))
    f.close()


def delete(megs):
    with open(enviroment.info) as f:
        info = json.loads(f.read())
    f.close()
    try:
        for i in megs:
            channel = i.decode('GBK')  # 频道名
            channel_id = info['ids'][channel]  # 频道id
            if channel_id in info['urls']:
                info['urls'].pop(channel_id)
            if channel_id in info['paths']:
                info['paths'].pop(channel_id)
            if channel in info['names']:
                info['names'].remove(channel)
            if channel in info['ids']:
                info['ids'].pop(channel)
    except KeyError:
        print '频道名输入错误'
    else:
        with open(enviroment.info, 'w') as f:
            f.write(json.dumps(info))
        f.close()
