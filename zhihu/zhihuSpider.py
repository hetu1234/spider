# -*- coding: utf-8 -*-
import requests
import re
import time
import Image
from bs4 import BeautifulSoup as bs

import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

# page = requests.get("https://www.zhihu.com/topic/19554569/hot")
# print page

class LoginC:
    header_base = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com/',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'
    }

    _session = requests.session()

    def GetXSRF(self,url):

        hometext = self._session.get(url,headers=self.header_base).text
        # print self._session.get(url,headers=self.header_base).cookies
        homesoup = bs(hometext,'html.parser')
        xsfrinput = homesoup.find('input',{'name':'_xsrf'})
        print xsfrinput
        xsrftoken = xsfrinput['value']
        print '获取到到xsrf为： ',xsrftoken
        return xsrftoken

    def GetCaptcha(self,url):
        randomtime=str(int(time.time()*1000))
        captchaurl=url+'/captcha.gif?r='+randomtime+'&type=login'
        captcharesponse=self._session.get(captchaurl,headers=self.header_base)
        # print captcharesponse.text
        with open('checkcode.gif','wb') as f:
            f.write(captcharesponse.content)
            f.close()
        captcha=input('请输入验证码：')
        print captcha
        return captcha

    def GetCaptcha_cn(self, url):
        randomtime = str(int(time.time() * 1000))
        captchaurl = url + '/captcha.gif?r=' + randomtime + '&type=login&lang=cn'
        captcharesponse = self._session.get(captchaurl, headers=self.header_base)
        # print captcharesponse.text
        filename='checkcode_cn.gif'
        with open(filename, 'wb') as f:
            f.write(captcharesponse.content)
            f.close()
        im=Image.open(filename)
        # print im.format, im.size,im.size[0],im.size[1],im.mode,im

        captcha={}
        captcha['img_size']=list(im.size)
        index1=input('倒立汉字到序号： ')
        # print index1
        captcha['input_points']=self.GetPosByIndex(filename,list(index1))

        print captcha
        return captcha

    def GetPosByIndex(self,imgfile,il):
        """get pos of pixel by index
            :param imgfile: imput image file name
            :param index: the index of pose
            :return the list [left, top] of image file
        """
        img=Image.open(imgfile)
        print 'picture size: ',img.size
        width=img.size[0]/2
        higth=img.size[1]/2
        poslist=[]
        for index in il:
            if index<1 and index>7:
                print 'index = ',index,', is over [1,7]'
                return []
            left=width*(index-1)/8+width/(8*2)+8
            top=higth/2+8
            print left,top
            poslist.append([left,top])
        return poslist


    def login(self,baseurl,email,password):
        login_data={
            '_xrsf':self.GetXSRF(baseurl),
            'password':password,
            'remember_me':'true',
            'email':email,
        }
        login_data['captcha'] = self.GetCaptcha(baseurl)
        # login_data['captcha'] = self.GetCaptcha_cn(baseurl)
        loginurl = baseurl + '/login/email'
        loginresponse = self._session.post(loginurl, headers=self.header_base, data=login_data)
        print '服务器端返回响应码： ', loginresponse.status_code
        while loginresponse.json()['r']==1:
            login_data['captcha'] = self.GetCaptcha(baseurl)
            # login_data['captcha'] = self.GetCaptcha_cn(baseurl)
            loginresponse = self._session.post(loginurl, headers=self.header_base, data=login_data)

        print self._session.get(baseurl, headers=self.header_base).content



if __name__=='__main__':
    url=r"https://www.zhihu.com"

    lg=LoginC()
    lg.login(url,'wbk499@163.com','1qaz2wsx')


