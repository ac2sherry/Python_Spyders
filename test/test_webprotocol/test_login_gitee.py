#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
gitee 登陆
@Author: AC
2018-3-21
'''
__author__ = 'AC'

##############################################
#------------------import--------------------#
##############################################
import requests
from bs4 import BeautifulSoup
try:
    import cPickle as pickle
except:
    import pickle
##############################################
#------------------常量定义------------------#
##############################################
# agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'
agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:46.0) Gecko/20100101 Firefox/46.0'
headers = {
    'User-Agent': agent,
}
def load_user_info(filename):
    with open(filename) as f:
        username = f.readline().replace('\n', '')
        password = f.readline().replace('\n', '')
    return username, password

username, password = load_user_info('settings_gitee.txt')
##############################################
#------------------函数定义------------------#
##############################################
def get_authenticity_token(session):
    '''
    <meta content="authenticity_token" name="csrf-param" />
    <meta content="UTQf3UZni9YJ8AuViCC86WD8jkqD4fiSIHElvpIaX84=" name="csrf-token" />
    get token
    '''
    url = 'https://gitee.com/login'
    index_page = session.get(url, headers=headers)
    html_content = index_page.text
    soup = BeautifulSoup(html_content,'html.parser')
    # name 是find的定参，不能直接带入，需要建立attr
    token = soup.find('meta', attrs={'name':'csrf-token'})['content']
    return token

def isLogin(session):
    # 通过查看用户个人信息来判断是否已经登录
    url = "https://gitee.com/profile"
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False

def save_session(session):
    with open('gitee_session.txt', 'wb') as fout:
        pickle.dump(session.headers, fout)
        pickle.dump(session.cookies.get_dict(), fout)
        print('session 已写入文件')

def load_session():
    try:
        with open('gitee_session.txt', 'rb') as fout:
            headers = pickle.load(fout)
            cookies = pickle.load(fout)
            print('session 已写读取文件')
            return headers,cookies
    except:
        print('无session文件')
##############################################
#------------------类定义--------------------#
##############################################

##############################################
#------------------脚本开始------------------#
##############################################
if __name__ == '__main__':
    # 主线程
    session = requests.session()
    token = get_authenticity_token(session)
    print(token)

    postdata = {
        'authenticity_token' : token,
        'captcha' : None,
        'commit' : '登 录',
        'redirect_to_url' : None,
        'user[login]' : username,
        'user[password]' : password,
        'user[remember_me]' : 0,
        'utf8' : '✓',
    }
    login_url = 'https://gitee.com/login'
    login_page = session.post(login_url, data=postdata, headers=headers)
    # print(login_page.text)
    print(login_page.status_code)
    print(isLogin(session))

    # 保存cookie可以免二次登陆（这里是测试）
    save_session(session)
    headers, cookies = load_session()
    print(headers)
    print(cookies)