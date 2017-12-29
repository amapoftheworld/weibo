# -*- coding: utf-8 -*-

import re
import json
import base64
import binascii
import rsa
import requests
import io
# for test
import sys
sys.path.insert( 0, '..' )
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
from config import WBCLIENT, user_agent
from config import USER_NAME, PASSWD
from logger import logger

session = requests.session()
session.headers['User-Agent'] = user_agent

def encrypt_passwd(passwd, pubkey, servertime, nonce):  #rsa加密密码
    key = rsa.PublicKey(int(pubkey, 16), int('10001', 16)) #int('10001', 16) 并非要转换成16进制，而是说10001是16 进制的数，int函数要将其转化为十进制
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(passwd)
    passwd = rsa.encrypt(message.encode('utf-8'), key)
    return binascii.b2a_hex(passwd)

# 登录微博的流程
# 1.预登陆请求，获取到若干参数---> servertime、nonce、pubkey、rsakv
# 2.将获取到的以上4个参数连同不同方式加密的账户名密码一起封装进一个json中
# 3.带着参数data通过post请求进行登录操作

def wblogin():
    username = USER_NAME
    password = PASSWD
    resp = session.get(
        'http://login.sina.com.cn/sso/prelogin.php?'
        'entry=weibo&callback=sinaSSOController.preloginCallBack&'
        'su=%s&rsakt=mod&checkpin=1&client=%s' %
        (base64.b64encode(username.encode('utf-8')), WBCLIENT)
    )
    pre_login_str = re.match(r'[^{]+({.+?})', resp.text).group(1)  # 从返回的结果中匹配出json结果    [^{]用于匹配{前面的字符串 ({.+?})用于匹配{中的内容}

    pre_login = json.loads(pre_login_str)
    data = {
        'entry': 'weibo',
        'gateway': 1,
        'from': '',
        'savestate': 7,
        'userticket': 1,
        'ssosimplelogin': 1,
        'su': base64.b64encode(requests.utils.quote(username).encode('utf-8')),
        'service': 'miniblog',
        'servertime': pre_login['servertime'],
        'nonce': pre_login['nonce'],
        'vsnf': 1,
        'vsnval': '',
        'pwencode': 'rsa2',
        'sp': encrypt_passwd(password, pre_login['pubkey'],
                             pre_login['servertime'], pre_login['nonce']),
        'rsakv' : pre_login['rsakv'],
        'encoding': 'UTF-8',
        'prelt': '53',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.si'
               'naSSOController.feedBackUrlCallBack',
        'returntype': 'META'
    }

    resp = session.post(
        'http://login.sina.com.cn/sso/login.php?client=%s' % WBCLIENT,
        data=data
    )

    login_url = re.search('replace\\(\'([^\']+)\'\\)', resp.text).group(1)  # 正则表达式匹配(需要前面加\\

    resp = session.get(login_url)
    print(resp.text)
    login_str = re.search('\((\{.*\})\)', resp.text).group(1)

    login_info = json.loads(login_str)
    logger.info(u"登录成功：" + str(login_info))

    uniqueid = login_info["userinfo"]["uniqueid"]
    return (session, uniqueid)

if __name__ == '__main__':
    (http, uid) = wblogin()
    text = http.get('http://weibo.com/').text
    print(text)
