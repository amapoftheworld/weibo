# -*- coding: utf-8 -*-
__author__ = 'yyz'


from bs4 import BeautifulSoup
from logger import logger


##解析所有的热搜主页Url
def getHotUrl(html):
    soup=BeautifulSoup(html,'html.parser')
    soup_UrlP=soup.find_all(attrs={'class':'star_name'})
    urlList=[]
    for i in range(len(soup_UrlP)):
        url=soup_UrlP[i].a["href"]
        urlList.append("http://s.weibo.com"+url)
    return urlList


##解析所有热搜主页用户的mid ouid

def getMidAndOuid(html):
    soup=BeautifulSoup(html,'html.parser')
    soup_commentList=soup.find_all(attrs={'action-type':'feed_list_item'})
    listComment=[]
    for i in range(len(soup_commentList)):
        try:
            comment=soup_commentList[i]
            mid=comment['mid']
            ouid=comment['tbinfo'].split('=')[1]
            logger.info("mid："+mid+"---ouid:"+ouid)
            paras=mid+"@"+ouid#+"@"+pageid+"@"+key
            listComment.append(paras)
        except:
            logger.info("解析评论参数失败")
    return listComment

