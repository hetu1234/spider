#-*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup as BS
import MySQLdb
import traceback


class readOnePage:
    def __init__(self,baseurl,url):
        self.baseurl=baseurl
        self.url=url
        self._session=requests.session()
        self._text=self._session.get(self.url).text
        self._soup=BS(self._text)
        self.conn=None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn != None:
            self.conn.close()

    def findNext(self):
        """get next url"""
        urlNext=''
        htmlNext=None
        try:
            htmlNext=self._soup.find('ul',class_='pagination').find('span',class_='next').find_parent('a')
            if htmlNext != None:
                urlNext = self.baseurl + htmlNext['href']
        except AttributeError as e:
            urlNext=''
            print 'Error: ',e.message


        print 'urlNext=',urlNext
        return urlNext

    #read one article, containing author,[sex,age,]vote,comment,text
    def readOneArticle(self,text):
        # print type(unicode(text))
        soup=BS(unicode(text))
        name=''
        try:
            name=soup.find('h2').string.encode('utf-8')
        except Exception, e:
            name=''
            print 'name Error: ',e.message

        vote=0
        try:
            vote=int(soup.select('.stats-vote > [class~=number]')[0].text)
        except Exception,e:
            vote=0
            print 'vote Error: ',e.message

        comment=0
        try:
            comment=int(soup.select('.stats-comments > a > .number')[0].text)
        except Exception, e:
            comment=0
            print 'comment Error: ',e.message

        text=''
        try:
            text = soup.find('div',class_='content').find('span').text.encode('utf-8').strip()
        except Exception,e:
            text=''
            print 'text Error: ',e.message
        # print type(text)

        sexclass=soup.find('div',class_='articleGender')
        age=0
        sex=''
        if sexclass!=None:
            age = int(sexclass.text)
            try:
                pos = sexclass['class'].index('womenIcon')
                sex = 'F'
            except:
                sex = 'M'

        onelist=[name,sex,age,vote,comment,text]
        return onelist

    def readArticle(self):
        articlelist=self._soup.find_all('div',class_='article')
        # print type(articlelist[0])
        alllist=[]
        for article in articlelist:
            one=self.readOneArticle(article)
            #filter: text is null or vote less 1000, pass
            if one[5]!='' and one[3]>1000:
                alllist.append(one)

        # self.writeToFile(alllist)
        self.writeToMysql(alllist)

        print '----------------one page end--------------'

    def writeToFile(self,list):
        f = open('qiushi.txt', 'w')
        for one in list:
            oneline = one[0] + ', ' + one[1] + ',' + str(one[2]) + ', ' + str(one[3]) + ', ' + str(one[4]) + ', ' + one[5]
            f.write(oneline)
            f.write('\n')
        f.close()

    def writeToMysql(self,list):
        if self.conn == None:
            self.conn=MySQLdb.connect(host='localhost',user='dog',passwd='123456',db='bar',charset='utf8')
        cursor=self.conn.cursor()
        #create table if it is not exit
        sqlcreate='create table if not exists qiubai' \
                  '(id int(20) primary key AUTO_INCREMENT,' \
                  'name varchar(256) NOT NULL,' \
                  'sex varchar(6),' \
                  'age int(8),' \
                  'vote int(20),' \
                  'comment int(15),' \
                  'content text)'
        cursor.execute(sqlcreate)
        sqlinsert='insert into qiubai (name,sex,age,vote,comment,content) values(%s,%s,%s,%s,%s,%s)'
        for one in list:
            # print type(one[2])
            param=(one[0],one[1],one[2],one[3],one[4],one[5])
            n=cursor.execute(sqlinsert,param)
            # print n

        cursor.close()
        #must do this to commit change to mysql
        self.conn.commit()



if __name__=='__main__':
    url = r'http://www.qiushibaike.com'
    baseurl=r'http://www.qiushibaike.com'
    #to avoid url cycle
    allurl=[]
    while True:
        if url=='' or url in allurl:
            break
        allurl.append(url)
        page=readOnePage(baseurl,url)
        page.readArticle()
        url=page.findNext()
    print '=================end================='