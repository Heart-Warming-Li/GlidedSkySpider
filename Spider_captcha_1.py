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

# pycharm远程centos安装selenium的坑
# 首先下载google-chrome-stable_current_x86_64.rpm包，并yum install google-chrome-stable_current_x86_64.rpm安装
# https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
# 然后下载chromedriver的二进制包，此版本必须和google-chrome版本对应，否则报不符合版本。  然后把文件添加777权限并放入/usr/bin/中
# https://cdn.npm.taobao.org/dist/chromedriver/77.0.3865.40/chromedriver_linux64.zip
# 下载selenium推荐下载对应chromedriver版本的包， 可以在github上找到，或者下载chromedriver时看到对应的发布时间
import json
import os
import time

import requests
import random
from PIL import Image
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, \
    MoveTargetOutOfBoundsException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from serialization_cookies import CookiesSerialization, env
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

from cv2matchTemplate import TemplateGap


# 腾讯滑块验证码
class TxCaptcha(object):
    def __init__(self):
        self.cookies = CookiesSerialization()
        self.cookies.load_cookies()
        self.web_cookies = self.cookies.json_cookies()

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"')
        self.chrome_options.add_argument('Connection=Keep-Alive')
        self.chrome_options.add_argument('Host=glidedsky.com')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.load_cookies()
        self.left_gap = 92  # 图片左侧为固定的，是大概位置
        self.img_scale = 0.5  # 验证码图片与真实图片比例大约0.5

    def load_cookies(self):
        """
        从COOKIES_FILE_PATH中加载cookies，并添加给selenium
        :return:
        """
        self.driver.get('http://glidedsky.com/level/web/crawler-captcha-1')
        self.driver.delete_all_cookies()
        for name, value in self.web_cookies.items():
            self.driver.add_cookie({
                'domain': '.glidedsky.com',
                'httpOnly': False,
                'name': name,
                'path': '/',
                'secure': False,
                'value': value
            })

    def captcha_img_url(self):
        """
        获得滑块验证码图片的url地址， 分别是全图img_url['full']，有缺口图img_url['gap']，缺口图img_url['template']
        :return:
        """
        WebDriverWait(self.driver, 2).until(
            ec.presence_of_element_located((By.ID, "tcaptcha_iframe"))
        )
        self.driver.switch_to.frame(self.driver.find_element(By.XPATH, "//*[@id=\"tcaptcha_iframe\"]"))
        img_url = {}
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        script_text = soup.select("script")
        try:
            cdn_pic = script_text[2].get_text().split(',')
        except IndexError:
            return
        for cdn in cdn_pic:
            if "cdnPic1" in cdn:
                url = cdn.split('"')[1]
                url_split = url.split('_')
                img_url['gap'] = url
                img_url['full'] = f'{url_split[0]}_0_{url_split[2]}_0'
                img_url['template'] = f'{url_split[0]}_2_{url_split[2]}_0'
                return img_url

    def download_img(self, url, urls=None):
        """
        下载验证码图片
        :param url:   第几页的url，http://glidedsky.com/level/web/crawler-captcha-1?page=3
        :param urls:    验证码url是个字典，self.captcha_img_url()得到
        :return:
        """
        while_num = 3
        while while_num:
            self.driver.get(url)
            urls = self.captcha_img_url()
            while_num = 0 if urls else while_num - 1
        try:
            gap_img = requests.get(urls['gap'])
            full_img = requests.get(urls['full'])
            template_img = requests.get(urls['template'])
        except TypeError:
            return
        with open('gap.jpg', 'wb+') as gap:
            gap.write(gap_img.content)
        with open('full.jpg', 'wb+') as full:
            full.write(full_img.content)
        with open('template.jpg', 'wb+') as full:
            full.write(template_img.content)

    def get_gap(self, img1, img2):
        """
        获取缺口偏移量
        :param img1: 不带缺口图片full_img
        :param img2: 带缺口图片gap_img
        :return:
        """
        try:
            img1 = Image.open(img1)
            img2 = Image.open(img2)
        except OSError:
            return 486   # 随便写的，无非让程序一直进行下去
        for i in range(self.left_gap, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.is_pixel_equal(img1, img2, i, j):
                    return i
        return self.left_gap

    def get_img_scale(self, gap):
        """
        :param gap:   # 图片缺口处X轴的位置
        :return:        # 根据比例计算的X轴位置，页面展示的X轴位置
        """
        gap = (gap * self.img_scale) - (self.left_gap / 2)  # 图片左侧为固定的，根据比例计算后的大概位置
        return gap

    def is_pixel_equal(self, img1, img2, x, y):
        """
        判断两个像素是否相同
        :param img1: 图片1
        :param img2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pix1 = img1.load()[x, y]
        pix2 = img2.load()[x, y]
        threshold = 60
        if (abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(pix1[2] - pix2[2] <
                                                                                              threshold)):
            return True
        else:
            return False    # 只要x轴像素不一样，就说明从此处开始就是，缺口位置

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 1
        # 初速度
        v = 0

        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 2
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 0.5 * a * (t ** 2)
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        track.reverse()
        return track

    def get_slider(self, url):
        """
        得到滑块按钮对象
        :param url:     第几页的url，http://glidedsky.com/level/web/crawler-captcha-1?page=3
        :return:        滑块按钮的selenium对象
        """
        try:
            self.download_img(url)
            slider = self.driver.find_element_by_xpath('//*[@id="tcaptcha_drag_button"]')
            return slider
        except NoSuchElementException:
            return

    def move_to_gap(self, slider, track):
        """
        移动滑块到缺口位置
        :param slider:  滑块按钮的selenium对象
        :param track:   滑块移动的px值，是个list
        :return:
        """
        try:
            ActionChains(self.driver).click_and_hold(slider).perform()
        except StaleElementReferenceException:
            return
        try:
            for x in track:
                ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
        except MoveTargetOutOfBoundsException:
            return
        time.sleep(0.5)
        ActionChains(self.driver).release().perform()

    def refresh_captcha(self, url, full_img, gap_img, template_img):
        """
        刷新验证码
        :param url:          第几页的url，http://glidedsky.com/level/web/crawler-captcha-1?page=3
        :param full_img:     分别是全图
        :param gap_img:      有缺口图
        :param template_img:  缺口图
        :return:
        """
        self.driver.refresh()
        slider = self.get_slider(url)
        if os.path.getsize(full_img) > 0:
            gap = self.get_gap(full_img, gap_img)
        else:
            os.remove(full_img)
            tmp = TemplateGap()
            gap = tmp.get_gap(gap_img, template_img)
        gap = self.get_img_scale(gap)
        track = self.get_track(gap)
        self.move_to_gap(slider, track)

    def get_num_html(self, url, full_img, gap_img, template_img):
        """
        获得验证通过的页面源码
        :param url:          第几页的url，http://glidedsky.com/level/web/crawler-captcha-1?page=3
        :param full_img:     分别是全图
        :param gap_img:      有缺口图
        :param template_img:  缺口图
        :return:        self.driver.page_source, 页面源码
        """
        try:
            time.sleep(3)
            window = self.driver.current_window_handle
            self.driver.switch_to.window(window)
            return self.driver.page_source
        except:
            print('异常重试')
            self.clean_jpg(full_img, gap_img, template_img)
            self.refresh_captcha(url, full_img, gap_img, template_img)
            window = self.driver.current_window_handle
            self.driver.switch_to.window(window)
            time.sleep(3)
            return self.driver.page_source

    @staticmethod
    def get_page_nums(html_content):
        """
        获得页面上需要的数字
        :param html_content:  页面源码
        :return:
        """
        all_num = []
        soup = BeautifulSoup(html_content, 'lxml')
        select = soup.select("div.col-md-1")
        for i in select:
            num = int(i.get_text().strip())
            all_num.append(num)
        return all_num

    def re_get_lost_page(self, lost_list):
        """
        重新获得第一次未获得的页面数据
        :param lost_list:   丢失页面的page列表
        :return:    所有丢失页面中数字和组成的列表，list
        """
        lost_list_page_nums = []
        cache_result = self.get_cache_result()
        if len(lost_list):
            print(f'开始打点以下丢失页的数据: {lost_list}')
            while lost_list:
                page = random.choice(lost_list)
                print(f'随机获取丢失页数据，当前为第{page}页')
                url = f'http://glidedsky.com/level/web/crawler-captcha-1?page={page}'
                nums = self.get_nums(url, full_img, gap_img, template_img)
                if len(nums) > 0:
                    lost_list_page_nums.append(sum(nums))
                    lost_list.remove(page)
                    cache_result_nums = cache_result['nums']
                    cache_result_nums.append(sum(nums))
                    cache_result.update({"lost": lost_list})
                    cache_result.update({'nums': cache_result_nums})
                    self.save_cache_result(cache_result)
                    print(f'还有以下未完成: {lost_list}')
                    print(f'丢失页面数据: {lost_list_page_nums}')
        return lost_list_page_nums

    def get_nums(self, url, full_img, gap_img, template_img):
        """
        获得每页的数字和
        :param url:          第几页的url，http://glidedsky.com/level/web/crawler-captcha-1?page=3
        :param full_img:     分别是全图
        :param gap_img:      有缺口图
        :param template_img:  缺口图
        :return:
        """
        slider = self.get_slider(url)
        if os.path.isfile(full_img) and os.path.getsize(full_img) > 0:
            # print('full size: ', os.path.getsize(full_img))
            if os.path.isfile(gap_img) and os.path.getsize(gap_img) == 0: self.download_img(url)
            gap = self.get_gap(full_img, gap_img)
        else:
            if os.path.isfile(full_img): os.remove(full_img)
            if os.path.isfile(gap_img) and os.path.getsize(gap_img) == 0 : self.download_img(url)
            tmp = TemplateGap()
            try:
                gap = tmp.get_gap(gap_img, template_img)
            except OSError:
                return []
        gap = self.get_img_scale(gap)
        track = self.get_track(gap)
        self.move_to_gap(slider, track)
        html_content = self.get_num_html(url, full_img, gap_img, template_img)
        nums = self.get_page_nums(html_content)
        return nums


    def save_cache_result(self, result):
        """
        缓存数据结果
        :param result:   {"page": 0,"lost": [],"nums": []},  初始数据
        :return:        # page 当前执行到第几页， lost未获取页的list，已经获取页数字的sum的list
        """
        cache_file = env('CAPTCHA_TRACK_CACHE_FILE', default='.captcha_track')
        with open(cache_file, 'w+', encoding='utf-8') as file:
            json.dump(result, file)

    def get_cache_result(self):
        """
        获取缓存数据的结果
        :return:
        """
        cache_file = env('CAPTCHA_TRACK_CACHE_FILE', default='.captcha_track')
        with open(cache_file, 'r+', encoding='utf-8') as text:
            result = json.load(text)
            return result

    def clean_jpg(self, full_img, gap_img, template_img):
        """
        清理上次执行获得的图片，避免污染下次滑块结果
        :param full_img:     分别是全图
        :param gap_img:      有缺口图
        :param template_img:  缺口图
        :return:
        """
        if os.path.isfile(full_img): os.remove(full_img)
        if os.path.isfile(gap_img): os.remove(gap_img)
        if os.path.isfile(template_img): os.remove(template_img)
        if os.path.isfile('template_invert.jpg'): os.remove('template_invert.jpg')

    def quit_driver(self):
        """
        执行完毕，退出程序
        :return:
        """
        print('开始退出程序')
        time.sleep(1)
        self.driver.quit()
        print('退出程序完毕')

    def main(self, page, full_img, gap_img, template_img):
        """
        程序执行入口
        :param page:    需要获取多少页数据，获取1000也，page为1000
        :param full_img:     分别是全图
        :param gap_img:      有缺口图
        :param template_img:  缺口图
        :return:
        """
        cache_result = self.get_cache_result()
        current_page = cache_result['page']
        lost_page = cache_result['lost']
        get_nums_sum = cache_result['nums']
        self.clean_jpg(full_img, gap_img, template_img)
        for p in range(current_page+1, page+1):
            save_cache = {}
            print(f'正在获取第{p}页数据')
            page_url = f'http://glidedsky.com/level/web/crawler-captcha-1?page={p}'
            self.clean_jpg(full_img, gap_img, template_img)
            page_nums = self.get_nums(page_url, full_img, gap_img, template_img)
            if len(page_nums) == 0:
                lost_page.append(p)
                print(f'没有正常获得页面数字的，page列表：{lost_page}')
            else:
                sum_page_nums = sum(page_nums)
                get_nums_sum.append(sum_page_nums)
                print(f'已经获取的页面数字和: {get_nums_sum}')
            save_cache['page'] = p
            save_cache['lost'] = lost_page
            save_cache['nums'] = get_nums_sum
            print(save_cache)
            self.save_cache_result(save_cache)
            self.clean_jpg(full_img, gap_img, template_img)
        re_lost_page_nums = self.re_get_lost_page(lost_page)
        print('所有页面总和： ', sum(get_nums_sum) + sum(re_lost_page_nums))


if __name__ == '__main__':
    # 3007729
    gap_img = 'gap.jpg'
    full_img = 'full.jpg'
    template_img = 'template.jpg'
    page_num = 1000
    tx = TxCaptcha()
    tx.main(page_num, full_img, gap_img, template_img)
    tx.quit_driver()
