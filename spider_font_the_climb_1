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
import base64
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
    bin_data = base64.decodebytes(base64_string.encode())
    with open('online.tff', "wb") as f:
        f.write(bin_data)
    return bin_data


# 把base64转换为xml文件
def convert_font_to_xml(bin_data):
    font = TTFont(BytesIO(bin_data))
    font.saveXML('online.xml')


# 替换源码数字与真实数字
def convert_font_num(nums):
    base_cid = {'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
                'six': '6', 'seven': '7', 'eight': '8', 'nine': '9'}  # 通过xml文件分析得到此结果
    online_font = TTFont('online.tff').getGlyphOrder()[1:]  # 获取GlyphOrder字段，经对比xml查看此字段是变化的，并且变化的映射关系(cmap)对应真实数字，cmap项不变化, glfy项变化
    real_num_list = []  # 保存替换后的数字
    for n in nums:
        base_cid_key = list(base_cid.keys())[list(base_cid.values()).index(n)]  # 根据字典value获取key值
        online_font_index = online_font.index(base_cid_key)  # 获取列表中对应值的下标
        real_num_list.append(str(online_font_index))
    real_num = ''.join(real_num_list)  # 组合替换后的每一个数字子
    return real_num


for page in range(1, 1001):
    get_html = session.get(f'http://glidedsky.com/level/web/crawler-font-puzzle-1?page={page}')
    print(f"开始获取第【{page}】页数据")
    # 第一种####################3315696
    soup = BeautifulSoup(get_html.text, "lxml")
    font_style = soup.select_one("style")   # 获取style标签中的base64值
    font_style = font_style.get_text()
    font_style_bs64 = font_style.split(',')[1].split(')')[0]
    make_font_file(font_style_bs64)         # 把base64转换为字体文件
    # convert_font_to_xml(make_font_file(font_style_bs64))  # 把base64转换为xml文件
    select = soup.select("div.col-md-1")    # 获取源码标签中对应的数字
    for i in select:
        num = i.get_text().strip()
        num = convert_font_num(num)
        all_num.append(int(num))
    print(f"已有数据: {all_num}")
print(sum(all_num))


# 第二种############################################
# 另外一种woff格式文件，此文件不同之处是没有glfy项并且只有cmap项变化， 跟上面刚好相反。
# base_cid = {'cid00017': '0', 'cid00018': '1', 'cid00019': '2', 'cid00020': '3', 'cid00021': '4', 'cid00022': '5',
#             'cid00023': '6', 'cid00024': '7', 'cid00025': '8', 'cid00026': '9'}
# onlineText = list('631')  # 源码中的数字
# onlineFont = TTFont('online.tff')  # 线上加载的字体文件
# onlineFontCmap = onlineFont.getBestCmap()  # {48: 'cid00022', 49: 'cid00021', 50: 'cid00023', 51: 'cid00020', 52: 'cid00026', 53: 'cid00018', 54: 'cid00017', 55: 'cid00025', 56: 'cid00024', 57: 'cid00019'}
# onlineFontCmap_New = {}  # {'0x30': 'cid00022', '0x31': 'cid00021', '0x32': 'cid00023', '0x33': 'cid00020', '0x34': 'cid00026', '0x35': 'cid00018', '0x36': 'cid00017', '0x37': 'cid00025', '0x38': 'cid00024', '0x39': 'cid00019'}
# for k, v in onlineFontCmap.items():
#     onlineFontCmap_New[hex(k)] = v   # 把key值10进制转换为16进制，刚好对应font.xml文件中的cmap值
# onlineFontCmap_NewId = [f'0x3{text}' for text in onlineText]   # 经过对比发现前缀0x3加上源码中的数字，刚好又跟font.xml文件中的cmap值对应
# onlineFormatText = [base_cid[onlineFontCmap_New[newId]] for newId in onlineFontCmap_NewId]  # 从基础模板中找出对应的数字
# print(onlineFormatText)
