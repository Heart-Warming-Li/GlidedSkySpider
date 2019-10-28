#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ------------------------------------- #
# @author   LiMengHao                   #
# @email    954172807@qq.com            #
# @qq       954172807                   #
# @wechat                               #
# @copyleft LiMengHao                   #
# ------------------------------------- #
"""
import time

import base64
import random
from fontTools.ttLib import TTFont, BytesIO

from serialization_cookies import CookiesSerialization, BeautifulSoup

# 加载序列化cookies
cookies = CookiesSerialization()
cookies.load_cookies()
session = cookies.session
session.headers = cookies.headers
session.cookies = cookies.deserialization_cookies()

# 保存转换后的数据，也就是页面看到的
all_num = []


# base64转换为二进制数据和保存为tff字体文件
def make_font_file(base64_string):
    """
    bs64格式转为字体文件
    :param base64_string: <style>xxxxx</style>
    :return:  把字体文件保存为xml时需要的二进制字串
    """
    bin_data = base64.decodebytes(base64_string.encode())
    with open('online2.tff', "wb+") as f:
        f.write(bin_data)
    return bin_data


# 把base64转换为xml文件
def convert_font_to_xml(bin_data):
    """
    把字体文件保存为xml
    :param bin_data:  二进制字串
    :return:
    """
    font = TTFont(BytesIO(bin_data))
    font.saveXML('online.xml')


def str_to_ten_ary(string):
    """
    把页面上的混淆字符串转为Unicode字符串，unicode转换为16进制， 最后转换为10进制，符合getBestCmap字典中的key
    :param string:  详详钱  -> ['\u8be6', '\u8be6', '\u94b1']  -> ['0x8be6', '0x8be6', '0x94b1'] -> [35814, 35814, 38065]
    :return:    [35814, 35814, 38065]  字符串转换为10进制格式
    """
    sixteen_to_ten_ary_list = []
    for s in string:
        unicode_str = s.encode('unicode-escape').decode()
        sixteen_ary = unicode_str.replace('\\u', '0x')
        sixteen_to_ten_ary_list.append(int(sixteen_ary, 16))
    return sixteen_to_ten_ary_list


# 替换源码数字与真实数字
def convert_font_num(ten_ary_list):
    """
    把页面混淆字体转换为真实数字， 返回数字
    :param ten_ary_list:    [35814, 35814, 38065]
    :return:    332
    """
    font = TTFont('online2.tff')
    online_font = font.getGlyphOrder()[1:11]  # 获取GlyphOrder字段，
    online_font_cmap = font.getBestCmap()    # 获取Cmap映射关系，字典格式
    real_num_list = []  # 保存替换后的数字
    for ten_ary in ten_ary_list:
        rep_unicode = online_font_cmap[ten_ary]
        real_num = online_font.index(rep_unicode)
        real_num_list.append(str(real_num))
    return ''.join(real_num_list)


for page in range(1, 1001):
    get_html = session.get(f'http://glidedsky.com/level/web/crawler-font-puzzle-2?page={page}')
    print(f"开始获取第【{page}】页数据")
    soup = BeautifulSoup(get_html.text, "lxml")
    font_style = soup.select_one("style")   # 获取style标签中的base64值
    font_style = font_style.get_text()
    font_style_bs64 = font_style.split(',')[1].split(')')[0]
    make_font_file(font_style_bs64)         # 把base64转换为字体文件
    # convert_font_to_xml(make_font_file(font_style_bs64))  # 把base64转换为xml文件
    select = soup.select("div.col-md-1")    # 获取源码标签中对应的数字
    for i in select:
        page_string = i.get_text().strip()
        page_string = str_to_ten_ary(page_string)
        page_nums_sum = convert_font_num(page_string)
        all_num.append(int(page_nums_sum))
    print(f"已有数据: {all_num}")
    random_time = random.uniform(0.5, 0.7)
    sleep_time = round(random_time, 2)
    time.sleep(sleep_time)
print(sum(all_num))     # ####################2438028

