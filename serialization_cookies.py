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
import json
import time
import os
import requests
from bs4 import BeautifulSoup

import environ

ROOT_DIR = (environ.Path(__file__) - 1)  # 当前目录

env = environ.Env()
env.read_env(str(ROOT_DIR.path(".env")))


class CookiesSerialization(object):
    def __init__(self):
        self.session = requests.Session()
        self.COOKIES_FILE_PATH = env('COOKIES_FILE_PATH', default='glidedsky_login_cookies.txt')
        self.email = env("EMAIL")
        self.password = env("PASSWORD")
        self.headers = {
            'Host': 'glidedsky.com',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        }
        self.session.headers = self.headers
        self.login_url = 'http://glidedsky.com/login'

    def token(self):
        login_get = self.session.get(self.login_url)
        soup = BeautifulSoup(login_get.text, "lxml")
        select = soup.select_one("input[name='_token']")
        token = select.get('value')
        return token

    def serialization_cookies(self):
        """
        序列化cookies
        :return:
        """
        data = {
            "_token": self.token(),
            "email": self.email,
            "password": self.password
        }
        try:
            response = self.session.post(self.login_url, data=data)
            response.raise_for_status()
        except Exception as e:
            print('登陆失败')
            raise e

        cookies_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
        with open(self.COOKIES_FILE_PATH, 'w+', encoding='utf-8') as file:
            json.dump(cookies_dict, file)
            print('保存cookies文件成功！')

    def deserialization_cookies(self):
        """
        反序列化cookies
        :return:
        """
        with open(self.COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
            cookies_dict = json.load(file)
            cookies = requests.utils.cookiejar_from_dict(cookies_dict)
            return cookies

    def json_cookies(self):
        """
        不序列化cookies，直接是json格式
        :return:
        """
        with open(self.COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
            cookies_dict = json.load(file)
            return cookies_dict

    def get_nick_name(self):
        self.session.cookies = self.deserialization_cookies()
        response = self.session.get('http://glidedsky.com/level/web/crawler-basic-1')
        soup = BeautifulSoup(response.text, 'lxml')
        nick_name = soup.select_one("#navbarDropdown")
        nick_name = nick_name.get_text().strip()
        return nick_name

    def load_cookies(self):
        # 1、判断cookies序列化文件是否存在
        if os.path.exists(self.COOKIES_FILE_PATH):
            # 2、加载cookies
            print('加载已有的cookies文件')
        else:
            self.serialization_cookies()
            time.sleep(1)
            print('加载刚刚生成cookies文件')
        # 3、判断cookies是否过期
        try:
            nick_name = self.get_nick_name()
            print(f"你的昵称为: {nick_name}")
        except Exception as e:
            os.remove(self.COOKIES_FILE_PATH)
            print('cookies过期，重新生成cookies文件！')
            self.load_cookies()
