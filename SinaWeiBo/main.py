# -*- coding: utf-8 -*-
__author__ = 'yyz'

from selenium import webdriver
import time
import requests
from logger import logger
import parseUtils
import json
import random
user_agent = (
      'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
)
session = requests.session()
session.headers['User-Agent'] = user_agent



#使用selenium
driver = webdriver.Chrome(executable_path="D:\\Python34\\Scripts\\chromedriver.exe") #注意这里使用的是google chromedriver，很容易下载
driver.maximize_window()



##将浏览器中能看到的cookie转化为python中的字典
def get_cookie():
    with open("../cookie.txt") as f: #此处要将登陆后的cookie复制到cookie.txt，当然以为可以不这么做。程序中有个weiboLogion.py，会有写好的新浪微博登陆方式
        cookies={}
        for line in f.read().split(';'):
            name,value=line.strip().split('=',1)
            cookies[name]=value
        if(len(cookies)==0):
            logger.info("请输入登录后cookie")
        return cookies

#通过phantomjs将前端页面全部加载下来
def weibo_AliPay():
    x=0
    try:
        driver.get("https://weibo.com/")#进入微博主页
        time.sleep(15)
        driver.get("http://s.weibo.com/top/summary?Refer=top_hot&topnav=1&wvr=6")#打开热搜列表页
        time.sleep(5)
        urlList=parseUtils.getHotUrl(driver.page_source) #获取每个热搜对应的主页
        cj = requests.utils.cookiejar_from_dict(get_cookie())
        session.cookies = cj
        time.sleep(10)
        for i in range(len(urlList)):#全部热搜 len(urlList))
            try:
                driver.get(urlList[i])
                time.sleep(10)
                singlePage=driver.page_source
                cList=parseUtils.getMidAndOuid(singlePage) #获取mid、ouid
                logger.info(cList)
                for j in range(len(cList)):
                    strs=cList[j].split("@")
                    mid=strs[0]
                    ouid=strs[1]
                    t = time.time()
                    CommendUrl="http://s.weibo.com/ajax/comment/add?__rnd="+str(int(round(t * 1000)))
                    data = {
                        'act':'post',
                        'mid':mid,
                        'uid':ouid,
                        'forward':0,
                        'isroot':0,
                        'content':'（支付宝） 这个码都是10元以上的，骗人没有小丁丁， kLOJqP18bz',
                        'pageid':'weibo',
                        'dom':'[object HTMLElement]',
                        '_t':0
                    }
                    rep1=session.post(  #发起评论
                                      url=CommendUrl,
                                      headers={
                                     'Referer':urlList[i] ,
                                     'Host':"s.weibo.com"
                                      },
                                      data=data
                                    )
                    logger.info(rep1.text)
                    jsonH=json.loads(rep1.text)
                    if(jsonH['code']=="100000"):#如果返回码为1000代表评论成功
                        x=x+1
                        logger.info("第"+str(x)+"个用户评论成功")
                    time.sleep(random.randint(1, 5))

            except  Exception as err:
                logger.info("打开链接失败,Url:"+urlList[i]+","+str(err))
            time.sleep(300)
    except Exception as err:
         logger.info("出错啦，"+str(err))









if __name__ == '__main__':
    weibo_AliPay()




