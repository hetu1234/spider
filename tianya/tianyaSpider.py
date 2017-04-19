#-*-coding:utf-8-*-
import requests
from bs4 import BeautifulSoup
import chardet
import MySQLdb


class tianyaSpider:
    def __init__(self,baseurl):
        self.baseurl=baseurl
        self._sesson=requests.session()
        self.urllist=[]
        self.conn=None

    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     if self.conn != None:
    #         self.conn.close()

    def readUl(self,ultext):
        lilist = ultext.find_all('li')
        for li in lilist:
            try:
                href=li.find('a')['href']
                title=li.find('a').text.encode('utf-8')

                # print title,': ',self.baseurl+href
                self.urllist.append([title,self.baseurl+href])
            except Exception,e:
                print "Error: ",e.message

    def readNavChild(self,navchild):
        navlist = navchild.find_all('ul',class_='nav_child')
        for nav in navlist:
            self.readUl(nav)

    def readLeft(self,url):
        """read left navigate of page"""
        sesson=self._sesson.get(url)
        soup=BeautifulSoup(sesson.text)
        lefttext = soup.find('div',id='left')
        leftlist = lefttext.find_all('div',class_='nav_child_box')
        for ll in leftlist:
            # print '=============',type(ll),'============='
            self.readNavChild(ll)

    def readMain(self,url):
        """read main text in page"""
        sesson=self._sesson.get(url)
        soup=BeautifulSoup(sesson.text)
        maintext=soup.find('div',id='main')
        sortext=maintext.find('div',class_='tab-list').find('li',class_='more').find_all('dd')
        sorturl=r''
        keystr='排行'
        for text in sortext:
            if text.find('a').text.encode('utf-8').find(keystr) != -1:
                sorturl=self.baseurl+text.find('a')['href']
                # print sorturl
                self.readRank(sorturl)

    def readRank(self,url):
        """read rank page"""
        session=self._sesson.get(url)
        soup=BeautifulSoup(session.text)
        ranklist=soup.find('div',id='main').find('div',class_='type-list').find_all('a')
        keystr='总'
        rankurl=r''
        for rank in ranklist:
            if rank.text.encode('utf-8').find(keystr) != -1:
                rankurl=self.baseurl+rank['href']
                print rankurl
                self.readRankText(rankurl)

    def readRankText(self,url):
        session=self._sesson.get(url)
        soup=BeautifulSoup(session.text)
        ranktext=soup.find('div',id='main').select('div[class=mt5] > table')[0].select('tbody > tr')
        textlist=[]
        for text in ranktext:
            #delete head
            if text.find('th'):
                continue
            tdlist = text.find_all('td')

            name=tdlist[0].find('a').text.encode('utf-8')
            arturl=self.baseurl+tdlist[0].find('a')['href']
            author = tdlist[1].find('a').text.encode('utf-8')
            vote=int(tdlist[2].text)
            reply=int(tdlist[3].text)
            time=tdlist[4]['title']
            textlist.append([name,author,vote,reply,time,arturl])
            # print name,',' ,arturl,', ',author,', ',vote,', ',reply,', ',time

        # print textlist
        self.writeToMysql(textlist)
        print '--------end----------'

    def writeToMysql(self,alllist):
        if self.conn==None:
            self.conn=MySQLdb.connect(user='dog',passwd='123456',db='bar',charset='utf8')
            self.conn.autocommit(True)

        cursor=self.conn.cursor()
        sqlcreate='create table if not exists tianya (' \
                  'id int not null AUTO_INCREMENT,' \
                  'name varchar(1024) not null,' \
                  'author varchar(256),' \
                  'vote int,' \
                  'reply int,' \
                  'time varchar(24),' \
                  'url varchar(128),' \
                  'primary key (id,url))'
        cursor.execute(sqlcreate)
        sqlinsert='insert into tianya(name,author,vote,reply,time,url) values(%s,%s,%s,%s,%s,%s)'
        for list in alllist:
            parser=(list[0],list[1],list[2],list[3],list[4],list[5])
            cursor.execute(sqlinsert,parser)

        cursor.close()
        # self.conn.autocommit()

if __name__=='__main__':
    baseurl=r'http://bbs.tianya.cn'
    url=r''

    ty=tianyaSpider(baseurl)
    ty.readLeft(baseurl)
    for url1 in ty.urllist:
        if url1[0].find('论史') != -1:
            print url1[1]
            url=url1[1]

    ty.readMain(url)