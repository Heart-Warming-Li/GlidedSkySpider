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
import re

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
    get_html = session.get(page_url)
    # with open('4.html', 'w+', encoding='utf-8') as h:
    #     h.write(get_html.text)
    soup = BeautifulSoup(get_html.text, "lxml")
    font_style = soup.select_one("style")   # 获取style标签中的值
    font_style = font_style.get_text().strip()
    # with open('css.css', 'w+', encoding='utf-8') as f:
    #     f.write(font_style)
    select = soup.select("div.col-md-1")    # 获取源码标签中对应的数字
    class_text = dict()  # {'BQF0gVcv': '', 'FMDm1NfsV': '', 'QJwg2ecB': '2', 'acgg3suCU': '5', 'dRC4jExW': '1', 'hzur5YEqQZ': '7', 'Fh6TYMD': '', 'ObR7RbjCo': '', 'PB8Mdlc': '9', 'flh9FycR': '5', 'AVpEi10aYqzo': '8', 'eGB11YCnI': '', 'TIXNx12YMjxF': '5', 'rA13swye': '', 'Fe14QSFj': '1', 'ND15gKF': '2', 'iSWz16MMv': '2', 'uPYR17Ktsk': '8', 'bgdc18oDaB': '', 'mKuW19pyNO': '8', 'AKVb20Ves': '2', 'Iz21uzF': '2', 'esPp22HLIy': '5', 'Zi23BuO': '5', 'JmpX24Esvsm': '1', 'pu25FTU': '6', 'YzdZN26fBuY': '0'}
    page_tag = dict()  # {0: ['BQF0gVcv'], 1: ['FMDm1NfsV'], 2: ['QJwg2ecB', 'acgg3suCU', 'dRC4jExW'], 3: ['hzur5YEqQZ', 'Fh6TYMD'], 4: ['ObR7RbjCo'], 5: ['PB8Mdlc', 'flh9FycR'], 6: ['AVpEi10aYqzo', 'eGB11YCnI'], 7: ['TIXNx12YMjxF', 'rA13swye'], 8: ['Fe14QSFj', 'ND15gKF', 'iSWz16MMv'], 9: ['uPYR17Ktsk', 'bgdc18oDaB'], 10: ['mKuW19pyNO', 'AKVb20Ves', 'Iz21uzF', 'esPp22HLIy'], 11: ['Zi23BuO', 'JmpX24Esvsm', 'pu25FTU', 'YzdZN26fBuY']}
    i = 0
    for content in select:
        tag = []
        for c in content.contents:
            try:
                class_text[c.get('class')[0]] = c.get_text().strip()
                tag.append(c.get('class')[0])
            except AttributeError:
                pass
        page_tag[i] = tag
        i += 1
    return page_tag, font_style, class_text


def remove_opacity(page_css, style_name):
    """
    :param page_css:     源码中<style></style>标签中的css样式
    :param style_name:   每个<div class="col-md-1"></div>中包含的所有css样式class名字 ['QJwg2ecB', 'acgg3suCU', 'dRC4jExW']
    :return:    去除样式有opacity属性的style_name,并返回style_name
    """
    for name in style_name:
        try:
            re.compile(r'\.%s(.*?) { opacity:(.*?) }' % name).search(page_css).group(2)
            style_name.remove(name)
        except AttributeError:
            pass
    return style_name


def style_index(style_name, font_style, class_text):
    """
    :param style_name:  page_tag 中的  ['QJwg2ecB', 'acgg3suCU', 'dRC4jExW']
    :return:    替换后,页面显示的数字
    """
    real_num = []   # 位置转换后的结果
    # with open('css.css', 'r') as f:
    #     font_style = f.read()
    style_name = remove_opacity(page_css=font_style, style_name=style_name)
    left_before = []    # 每个<div>中class属性对应的css不一定有left和content属性，但是还会有位置偏移，此处标记位置偏移记录
    for name in style_name:
        try:
            left = re.compile(r'\.%s(.*?) { left:(.*?) }' % name).search(font_style).group(2)  # 查看class是否包含left:1em属性
            left_before.append(1)
        except AttributeError:
            left_before.append(0)
            left = False
        try:
            before = re.compile(r'\.%s(.*?) { content:(.*?) }' % name).search(font_style).group(2)  # 查看class是否包含content属性
            left_before.append(1)
        except AttributeError:
            left_before.append(0)
            before = False
        name_value = class_text[name]   # 获取每个class属性对应的源码结果<div class="QJwg2ecB">2</div>，也就是2
        if left:
            name_index = left.strip().split('em')[0]
            name_index = int(name_index)
            real_num.insert(name_index, name_value)  # 对位置偏移进行排序
        elif before:
            name_index = before.strip().split('"')[1]
            name_index = int(name_index)
            return name_index                        # 没有位置偏移直接返回content内容
        else:
            if sum(left_before) == 0 or sum(left_before) == 2:
                real_num.append(name_value)          # 对位置偏移进行排序
            else:
                real_num.insert(0, name_value)       # 对位置偏移进行排序
    real_num = ''.join(real_num)
    real_num = int(real_num)
    return real_num


def main(page_tag, font_style, class_text):
    page_nums = []
    for _, tags in page_tag.items():
        css_position = style_index(tags, font_style=font_style, class_text=class_text)
        page_nums.append(css_position)
    return page_nums


if __name__ == '__main__':
    all_pages_nums = []
    for page in range(1, 3):
        url = f'http://glidedsky.com/level/web/crawler-css-puzzle-1?page={page}'
        page_tag, font_style, class_text = get_css_style(url)
        page_nums = main(page_tag=page_tag, font_style=font_style, class_text=class_text)
        all_pages_nums.append(sum(page_nums))   # 每页返回的是列表，因此先对每页数据进行sum计算，然后插入list，最后再做所有页面数据求和
        print(f'获取第 [{page}] 数据:  {page_nums}')
        print(f'每页数据sums值:  {all_pages_nums}\n')
    print(all_pages_nums)
    print(sum(all_pages_nums))  # 2753395
