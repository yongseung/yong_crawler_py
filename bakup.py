# -*-coding:utf-8

from bs4 import BeautifulSoup
import time
import traceback
import urllib.request
import urllib.robotparser as rb
import re
import os
import sqlite3
import csv

abc = 500

crawler_name = "my_crawler"
mainpage = "https://www.rocketpunch.com/jobs/9505"
mainpath = './mymydata/'


def getContent(url, delay=0):
    time.sleep(delay)
    print("in def",url)

    if not rb.RobotFileParser().can_fetch("*", url):
        print("This is rejected", url)
        return None

    try:

        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', crawler_name)]
        contents = opener.open(url).read().decode("utf-8")


    except:
        traceback.print_exc()
        return None

    return contents


def getArticleInfo(soup):
    "get article info"

    rBlog = re.compile('.+blog.daum.net/\w+/\d+.*?')
    URLs = soup('a',{'href':rBlog})

    return [ u.get('href').split('?')[0] for u in URLs]


def getOwnArticles(contents):
    " get this list of story"
    ret = []
    soup = BeautifulSoup(contents)
    rBlog = re.compile('.+/BlogView.+')
    for u in soup('a',{'href':rBlog}):
        href = u.get('href')
        article = href.split('articleno=')[1].split('&')[0]
        if ret.count(article)<1:
            ret.append(article)

    return ret


def gatherNeighborInfo(soup):
    "이웃 블로거/혹은 다녀간 블로거 정보를 수집합니다."

    #daum blog 관련 주소를 찾습니다.
    rBlog = re.compile('http://blog.daum.net/|w+')
    Neighbors = soup('a',{'href':rBlog})
    cnt = 0
    for n in Neighbors:
        url = n.get('href')
        blogname = url.split('/')[-1]
        if url and url.startswith('http://') and db.isCrawledURL(url)<1:
            db.insertURL( url, 1 )

            url2 = getRedirectedURL(url)
            if not url2: continue
            re_url = 'http://blog.daum.net' + url2
            body = getContent(re_url, 0)
            if body:
                for u in getOwnArticles(body):
                    #자신의 글 주소를 db에 저장합니다.
                    fullpath = 'http://blog.daum.net/'+blogname+'/'+u
                    cnt += db.insertURL(fullpath)
    if cnt>0: print('%d neighbor articles inserted'%cnt)

def getRedirectedURL(url):
    "본문에 해당하는 프레임의 url을 얻어옵니다."
    contents = getContent(url)
    if not contents: return None

    #redirect
    try:
        soup = BeautifulSoup(contents)
        frame = soup('frame')
        src = frame[0].get('src')
    except:
        src = None
    return src

def getBody(soup, parent):
    "본문 텍스트를 구합니다."

    #본문 주소를 포함한 iframe을 찾습니다.
    rSrc = re.compile('.+/ArticleContentsView.+')
    iframe = soup('iframe',{'src':rSrc})
    if len(iframe)>0:
        src = iframe[0].get('src')
        iframe_src = 'http://blog.daum.net'+src

        #그냥 request하면 안 되고, referer를 지정해야 browser를 통해 요청한 것으로 인식합니다.
        req = urllib.request.Request(iframe_src)
        req.add_header('Referer', parent)
        body = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(body)
        return str(soup.body)
    else:
        print('NULL contents')
        return ''

def parseArticle(url):
    "해당 url을 parsing하고 저장합니다."

    #blog id와 article id를 얻습니다.
    article_id = url.split('/')[-1]
    blog_id = url.split('/')[-2]

    #redirect된 주소를 얻어 옵니다.
    newURL = getRedirectedURL(url)

    if newURL:
        try:
            #blog 디렉터리를 만듭니다.`
            os.mkdir(mainpath+blog_id)
            print("make dir")
        except:
            #디렉터리를 만들다 에러가 난 경우 무시합니다.
            pass

        newURL = 'http://blog.daum.net'+newURL
        contents = getContent(newURL, 0)
        if not contents:
            print('Null Contents...')
            #해당 url이 유효하지 않은 경우 에러(-1)로 표시합니다.
            db.updateURL(url, -1)
            return

        #HTML을 파싱합니다.
        soup = BeautifulSoup(contents)

        #이웃 블로거 정보가 있나 확인합니다.
        gatherNeighborInfo(soup)

        #블로그 URL이 있을 경우 db에 삽입합니다.
        n=0
        for u in getArticleInfo(soup):
            n += db.insertURL(u)
        if n>0: print('inserted %d urls from %s'%(n,url))

        #title을 얻습니다.
        sp = contents.find('<title>')
        if sp>-1:
            ep = contents[sp+7:].find('<title>')
            title = contents[sp+7:sp+ep+7]
        else:
            title = ''

        #본문 HTML을 보기 쉽게 정리합니다.
        contents = getBody(soup, newURL)

        #script를 제거합니다.
        pStyle = re.compile('<style(.*?)>(.*?)</style>', re.IGNORECASE | re.MULTILINE | re.DOTALL )
        contents = pStyle.sub('', contents)
        pStyle = re.compile('<script(.*?)>(.*?)</script>', re.IGNORECASE | re.MULTILINE | re.DOTALL )
        contents = pStyle.sub('', contents)
        pStyle = re.compile("<(.*?)>", re.IGNORECASE | re.MULTILINE | re.DOTALL )
        contents = pStyle.sub('', contents)

        #txt file을 저장합니다.
        fTXT = open( mainpath + blog_id + '/' + article_id + '.txt', 'w',encoding='utf-8')
        fTXT.write( title+'|n')
        fTXT.write(contents)
        fTXT.close()

        #처리했다고 db에 표시합니다.
        db.updateURL(url)

    else:
        print('Invalid blog article...')
        #해당 url이 유효하지 않은 경우 에러(-1)로 표시합니다.
        db.updateURL(url, -1)

class DB:
    "SQLITE3 wrapper class"
    def __init__(self):
        self.conn = sqlite3.connect('crawlerDB')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS urls(url text, state int)')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS IDX001 ON urls(url)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS IDX002 ON urls(state)')

    def __del__(self):
        self.conn.commit()
        self.cursor.close()

    def insertURL(self, url, state=0):
        try:
            self.cursor.execute("INSERT INTO urls VALUES (?,?)", (url,state))
            self.conn.commit()
        except:
            return 0
        else:
            return 1

    def selectUncrawledURL(self):
        self.cursor.execute('SELECT * FROM urls where state=0')
        return [ row[0] for row in self.cursor.fetchall() ]

    def updateURL(self, url, state=1):
        self.cursor.execute("UPDATE urls SET state=? WHERE url=?" , (state,url) )

    def isCrawledURL(self, url):
        self.cursor.execute("SELECT COUNT(*) FROM urls WHERE url=? and state=1", (url,))
        ret = self.cursor.fetchone()
        return ret[0]

db = DB()

if __name__ == '__main__':
    print('starting crawl...')
    cnt = 10200
    mainpage = "https://www.rocketpunch.com/jobs/"

    mainurl = mainpage+str(cnt)

  #  fTXT = open(mainpath +'rpunch' +'.txt', 'w', encoding='utf-8')

    contents = urllib.request.urlopen(mainurl)
    soup = BeautifulSoup(contents)

    csv_file = open('rpunch.csv','w')
    cw = csv.writer(csv_file,  delimiter=',')

    y=10
    if (lambda y: y)(y) :
        print(y)

    total = []
    pat_money = re.compile(r'.*만원')
    pat_last = re.compile(r'.*채용 페이지')
    while True:
        try:
            cnt += 1
            mainurl = mainpage + str(cnt)
            print(cnt)
            contents = urllib.request.urlopen(mainurl)
            soup = BeautifulSoup(contents)
            pannel = soup.find_all('div' , attrs={'class':'wrap_wide'})
            date = soup.find_all('p', attrs={'class':'p date'},text=True)[0].text
            inform = pannel[2].find_all(text=True)
            temp = []
            temp.append(date)
            #print(pannel[2].find_all(text=True))
            for summary in inform:

                if summary == "채용 삭제":
                    print("yoyo")
                    break
                elif bool(pat_last.findall(summary)):
                    print("lambda")
                    break
                elif bool(pat_money.findall(summary)):
                    temp.append(summary)
                    break
                temp.append(summary)

            print(temp)

            skills = []
            for ultag in soup.find_all('ul', attrs={'class': 'list-unstyled list-tags'}):
                for litag in ultag.find_all('li'):
                    skills.append(litag.text)

            if len(skills):
                print("skill upgrade")
                temp.append(skills)

            cw.writerow(temp)

            if cnt >10230:
                break
        except:
            cnt= cnt+1
            pass

    csv_file.close()
