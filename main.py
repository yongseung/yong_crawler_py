# -*-coding:utf-8

from bs4 import BeautifulSoup
import urllib.request
import re
import csv


if __name__ == '__main__':
    print('starting crawl...')
    cnt = 12193
    mainpage = "https://www.rocketpunch.com/jobs/"

    csv_file = open('rpunch.csv','w')
    cw = csv.writer(csv_file,  delimiter=',')

    # 만원 또는 채용 페이지 만나면 다음 데이터 가져오기
    pat_money = re.compile(r'.*만원')
    pat_last = re.compile(r'.*채용 페이지')

    while True:
        try:
            print("continue..")
            cnt -= 1
            mainurl = mainpage + str(cnt)

            contents = urllib.request.urlopen(mainurl)
            soup = BeautifulSoup(contents)
            pannel = soup.find_all('div' , attrs={'class':'wrap_wide'})
            date = soup.find_all('p', attrs={'class':'p date'},text=True)[0].text
            inform = pannel[2].find_all(text=True)

            #temp 에 담아 csv 에 파일 쓰기
            temp = []
            temp.append(date)
            for summary in inform:

                if summary == "채용 삭제":
                    break
                elif bool(pat_last.findall(summary)):
                    break
                elif bool(pat_money.findall(summary)):
                    temp.append(summary)
                    break
                temp.append(summary)


            #필요 스킬 따로 나옴
            skills = []
            for ultag in soup.find_all('ul', attrs={'class': 'list-unstyled list-tags'}):
                for litag in ultag.find_all('li'):
                    skills.append(litag.text)

            if len(skills):
                temp.append(skills)

            cw.writerow(temp)
            if cnt < 11000:
                break
        except:
            # 페이지 없는 경우 무시하고 다음 페이지
            cnt= cnt-1
            pass

    print("complete")
    csv_file.close()