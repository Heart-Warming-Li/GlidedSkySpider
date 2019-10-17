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
# from lxml import etree  # 第二种
from serialization_cookies import CookiesSerialization, BeautifulSoup

cookies = CookiesSerialization()
cookies.load_cookies()
session = cookies.session
session.headers = cookies.headers
session.cookies = cookies.deserialization_cookies()
get_html = session.get('http://glidedsky.com/level/web/crawler-basic-1')
# 第一种############################################################################276611
soup = BeautifulSoup(get_html.text, "lxml")
select = soup.select("div.col-md-1")
num = [int(i.get_text().strip()) for i in select]
print(sum(num))


# 第二种############################################################################276611
# get_html.encoding = get_html.apparent_encoding
# html = etree.HTML(get_html.text)
# content = html.xpath('//*[@id="app"]/main/div/div/div/div/div/text()')
# num = [int(i.strip().replace('\n', '')) for i in content]
# print(sum(num))
