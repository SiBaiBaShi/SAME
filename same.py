# -*- coding: UTF-8 -*-
# 处理输入指令
import time
import argparse
# 以下为自建模块
import info
import downlaod
import build_index
num_of_image = 0


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='python %(prog)s [options]',
                                     description=u'same应用图片下载\n'
                                                 u'无任何参数则下载前一周预设频道的图片\n'
                                                 u'默认均保存于\Saved Pictures\same\\new\\'.encode('GBK'),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-a', nargs='*', default=[],
                        help=u'add,加入新的或更新预设频道信息；格式：“频道名 id 路径”'.encode('GBK'))
    parser.add_argument('-ad', nargs='?', const=False, default=True,
                        help=u'not add default,选择此选项则新频道不加入默认下载序列'.encode('GBK'))
    parser.add_argument('-b', nargs='*', default=[],
                        help=u'build,建立新的索引；格式：“频道名”'.encode('GBK'))
    parser.add_argument('-d', nargs='*', default=[],
                        help=u'delete,删除频道预设信息；格式：“频道名(1) 频道名(2)”'.encode('GBK'))
    parser.add_argument('-n', nargs='?', const=False, default=True,
                        help=u'not,若不下载图片，输入此提示符，无其它参数'.encode('GBK'))
    parser.add_argument('-c', nargs='*', default=[],
                        help=u'channel,频道名；格式：“频道名(1) 频道名(2)”'.encode('GBK'))
    parser.add_argument('-t', nargs='*', default=change_time(),
                        help=u'time,时间范围；格式：“年.月.日(1) 年.月.日(2)”'.encode('GBK'))
    parser.add_argument('-p', nargs='*', default={},
                        help=u'path,保存路径；格式：“频道(1) 路径(1) 频道(2) 路径(2)”'.encode('GBK'))
    args = parser.parse_args()

    if args.a:
        info.add(args.a, args.ad)
    if args.b:
        build_index.index(args.b[0])
    if args.d:
        info.delete(args.d)

    # args.n默认为True，若不下载时，输入“-n”即变为False
    if args.n:
        downlaod.download(args.c, args.t, args.p)
