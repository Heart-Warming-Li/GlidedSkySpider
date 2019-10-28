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
from io import BytesIO

import base64
import re
from PIL import Image

from serialization_cookies import CookiesSerialization, BeautifulSoup

cookies = CookiesSerialization()
cookies.load_cookies()
session = cookies.session
session.headers = cookies.headers
session.cookies = cookies.deserialization_cookies()


def get_css_style(page_url):
    """
    :param page_url:  每页的url
    :return:            # class_text 每个标签class对应的值也就是<div class="QJwg2ecB">2</div>
                        # page_tag   每个<div class="col-md-1"></div>中包含的所有css样式class名字
                        # font_style 源码中<style></style>标签中的css样式
    """
    # with open('4.html', 'r+', encoding='utf-8') as h:
    #     get_html = h.read()
    # soup = BeautifulSoup(get_html, "lxml")
    get_html = session.get(page_url)
    soup = BeautifulSoup(get_html.text, "lxml")
    font_style = soup.select_one("style")   # 获取style标签中的值
    font_style = font_style.get_text().strip()
    select = soup.select("div.col-md-1")    # 获取源码标签中对应的数字
    page_tag = dict()  # {0: ['BQF0gVcv'], 1: ['FMDm1NfsV'], 2: ['QJwg2ecB', 'acgg3suCU', 'dRC4jExW'], 3: ['hzur5YEqQZ', 'Fh6TYMD'], 4: ['ObR7RbjCo'], 5: ['PB8Mdlc', 'flh9FycR'], 6: ['AVpEi10aYqzo', 'eGB11YCnI'], 7: ['TIXNx12YMjxF', 'rA13swye'], 8: ['Fe14QSFj', 'ND15gKF', 'iSWz16MMv'], 9: ['uPYR17Ktsk', 'bgdc18oDaB'], 10: ['mKuW19pyNO', 'AKVb20Ves', 'Iz21uzF', 'esPp22HLIy'], 11: ['Zi23BuO', 'JmpX24Esvsm', 'pu25FTU', 'YzdZN26fBuY']}
    i = 0
    for content in select:
        tag = []
        for c in content.contents:
            try:
                tag.append(c.get('class')[0])
            except AttributeError:
                pass
        page_tag[i] = tag
        i += 1
    return page_tag, font_style


def img_threshold(font_style, threshold=250):
    image = re.compile(r'\.sprite { background-image:url(.*?) }').search(font_style).group(1)  # 查看background-image:url
    base64_img_str = image.split(',')[1].split('"')[0]

    img_fp = BytesIO(base64.b64decode(base64_img_str.encode('utf-8')))
    img = Image.open(img_fp)
    limg = img.convert('L')

    pixels = limg.load()

    for y in range(limg.height):
        for x in range(limg.width):
            pixels[x, y] = 0 if pixels[x, y] < threshold else 255

    return limg, pixels


def style_index(style_name, font_style):
    """
    :param style_name:  page_tag 中的  ['QJwg2ecB', 'acgg3suCU', 'dRC4jExW']
    :return:    替换后,页面显示的数字
    """
    position_before = {}
    for name in style_name:
        position = re.compile(r'\.%s(.*?) { background-position-x:(.*?)px }' % name).search(font_style).group(2)  # 查看class是否包含background-position-x:-2px属性
        position_before.update({name: int(position)})
    return position_before


def split_img_number(pixels, width, height):
    def find_next_white_column(start_x):
        for x in range(start_x, width):
            for y in range(height):
                if pixels[x, y] < 1:
                    break
            else:
                return x
        raise ValueError('split_img_number')

    def find_next_black_column(start_x):
        for x in range(start_x, width):
            for y in range(height):
                if pixels[x, y] < 1:
                    return x

    right_border_list = [0]
    black_start_x = find_next_black_column(0)
    # 0 right border

    white_start_x = find_next_white_column(black_start_x)
    right_border_list.append(white_start_x)
    for i in range(1, 10):
        black_start_x = find_next_black_column(white_start_x)
        white_start_x = find_next_white_column(black_start_x)
        right_border_list.append(white_start_x)

    return right_border_list


def combine_class_style(position_x, style_index, page_tag):
    """
    得到每一页面上的最终数字
    :param position_x:   PIL处理之后的position-x值列表
    :param style_index:  所有position-x值和class映射表，字典{"qN27pKMe": 0, "aAsKMe": -14, "sASJH92": -56}
    :param page_tag:     {0: ['BQF0gVcv'], 1: ['FMDm1NfsV'], 2: ['QJwg2ecB', 'acgg3suCU', 'dRC4jExW']}
    :return:    list
    """
    all_page_nums = []
    for _, tags in page_tag.items():
        tags_nums = []
        for tag in tags:
            tag_position_x = style_index[tag]
            for index, border_x in enumerate(position_x):
                cur_pos_x = abs(tag_position_x)
                if index + 1 >= len(position_x):
                    break
                if border_x <= cur_pos_x < position_x[index + 1]:
                    tags_nums.append(str(index))
                    break
        all_page_nums.append(int(''.join(tags_nums)))
    return all_page_nums


def main(url):
    all_style_index = {}
    page_tag, font_style = get_css_style(url)
    imgsrc, pixels = img_threshold(font_style)
    right_border_x_list = split_img_number(pixels, imgsrc.width, imgsrc.height)
    for _, tag in page_tag.items():
        position = style_index(tag, font_style)
        all_style_index.update(position)
    css_position = combine_class_style(right_border_x_list, all_style_index, page_tag)
    return css_position


if __name__ == '__main__':
    all_pages_nums = []
    for page in range(1, 1001):
        url = f'http://glidedsky.com/level/web/crawler-sprite-image-1?page={page}'
        page_nums = main(url)
        # print(page_nums)
        all_pages_nums.append(sum(page_nums))   # 每页返回的是列表，因此先对每页数据进行sum计算，然后插入list，最后再做所有页面数据求和
        print(f'获取第 [{page}] 数据:  {page_nums}')
        print(f'每页数据sums值:  {all_pages_nums}\n')
        time.sleep(0.2)
    print(sum(all_pages_nums))  # 2455535
    # print(main(''))
