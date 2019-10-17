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
# from lxml import etree
from serialization_cookies import CookiesSerialization, BeautifulSoup

cookies = CookiesSerialization()
cookies.load_cookies()
session = cookies.session
session.headers = cookies.headers
session.cookies = cookies.deserialization_cookies()

all_num = []
for page in range(1, 1001):
    get_html = session.get(f'http://glidedsky.com/level/web/crawler-basic-2?page={page}')
    # 第一种####################2511313
    soup = BeautifulSoup(get_html.text, "lxml")
    select = soup.select("div.col-md-1")
    for i in select:
        num = int(i.get_text().strip())
        all_num.append(num)

    # 第二种####################2511313
    # get_html.encoding = get_html.apparent_encoding
    # html = etree.HTML(get_html.text)
    # content = html.xpath('//*[@id="app"]/main/div/div/div/div/div/text()')
    # for i in content:
    #     new.append(int(i.strip().replace('\n', '')))
    print(f'runing page is {page} !')
    print(all_num)
print(sum(all_num))
