# -*-coding:utf-8

from bs4 import BeautifulSoup
import time
import traceback
import urllib.request
import urllib.robotparser as rb
import re
import sys
import os
import sqlite3

abc = 500

self.cursor.execute("CREATE TABLE IF NOT EXISTS urls(url text, state int)")
self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS IDX001 ON urls(url)")

self.cursor.execute("INSERT INTO urls VALUES ('%s',0)"%url)


crawler_name = "my crawler"
mainpage = "https://www.rocketpunch.com/"

print("rp is ")
print(
    rb.RobotFileParser().can_fetch("BBot", "http://blog.daum.net/robots.txt")
    , " yogo")


# robot paser
#

def getContent(url, delay=0.1):
    time.sleep(delay)
    print("in def",url)

    if not rb.RobotFileParser().can_fetch("*", url):
        print("This is rejected", url)
        return None

    try:

        print("tr")
        opener = urllib.request.build_opener()
        print("b")
        opener.addheaders = [('User-agent', crawler_name)]
        print("c")
        contents = opener.open(url).read().decode("utf-8")
        print("d")


    except:
        traceback.print_exc()
        return None

    return contents

my = getContent("http://blog.daum.net")

print(my)



if __name__ == '__main__':
    print('starting crawl...')

    #check mainpage
    contents = getContent( mainpage )
    URLs = getArticleInfo( BeatifulSoup(contents))

    print("main : "+URLs)
    nSuccess = 0
    for u in URLs:
        nSuccess += db.insertURL(u)
    print('inserted %d new page.'%nSuccess)

    while true:
        for u in db.selectUncrawledURL():
            print('downloading %s'%u)
            try:
                parseArticle(u)

            except:
                traceback.print_exc()
                db.updateURL(u, -1)
