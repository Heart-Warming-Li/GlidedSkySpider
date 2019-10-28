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
import ast
import time
import hashlib
import random

from serialization_cookies import CookiesSerialization, BeautifulSoup

# 加载序列化cookies
cookies = CookiesSerialization()
cookies.load_cookies()
session = cookies.session
session.headers = cookies.headers
session.cookies = cookies.deserialization_cookies()


all_page_nums_sum = []
for page in range(1, 1001):
    print(f"正在获取第{page}页")
    get_html = session.get(f'http://glidedsky.com/level/web/crawler-javascript-obfuscation-1?page={page}')
    soup = BeautifulSoup(get_html.text, "lxml")
    font_style = soup.select_one("main .container")  # 获取style标签中的base64值
    t = font_style.get('t')
    t = int((int(t) - 99) / 99)
    slat = f'Xr0Z-javascript-obfuscation-1{t}'.encode('utf-8')
    sign = hashlib.sha1(slat)
    sign = sign.hexdigest()
    ajax_url = f'http://glidedsky.com/api/level/web/crawler-javascript-obfuscation-1/items?page={page}&t={t}&sign={sign}'
    items = session.get(ajax_url)
    items = ast.literal_eval(items.text)
    page_nums = items['items']
    page_nums_sum = sum(page_nums)
    all_page_nums_sum.append(page_nums_sum)
    print('已获得page数字和为: ', all_page_nums_sum)
    random_time = random.uniform(0.5, 0.7)
    sleep_time = round(random_time, 2)
    time.sleep(sleep_time)

print('所有页面数字总和: ', sum(all_page_nums_sum))
# 2837717

# 备注： 此处难点主要在获取ajax的url地址以及，sign算法
# 通过在浏览器请求接口发现有sha1.min.js文件加载，并且有个不知所云的crawler-javascript-obfuscation-1.js文件
# 猜测问题出在这里，在sha1.min.js文件文件中打断点，最终运行到crawler-javascript-obfuscation-1.js文件中，是一个如下的代码
# let p = $('main .container').attr('p');
# let t = Math.floor(($('main .container').attr('t') - 99) / 99);
# let sign = sha1('Xr0Z-javascript-obfuscation-1' + t);
# $.get('/api/level/web/crawler-javascript-obfuscation-1/items?page=' + p + '&t=' + t + '&sign=' + sign, function (data)
# {
#     const list = JSON.parse(data).items;
#     $('.col-md-1').each(function (index) {
#         if (list && index < list.length) {
#             $('.col-md-1').eq(index).text(list[index])
#         }
#     })
# })

# 最终解析出加密方式为sha1('Xr0Z-javascript-obfuscation-1' + t);t为当前时间戳，也是页面中$('main .container').attr('t')的值
# 最后通过ajax请求获取到结果

