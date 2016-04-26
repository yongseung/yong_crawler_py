# -*-coding:utf-8
import mechanicalsoup
import csv
import argparse
import sys

br = mechanicalsoup.Browser()

class JobObject:
    company = 'X'
    name = ''
    rateWork = 'X'
    salary = 'X'
    recommend = 'X'
    untill = 'X'
    basic = []
    extra = []

    def clear(self):
        self.company = 'X'
        self.name = ''
        self.rateWork = 'X'
        self.salary = 'X'
        self.recommend = 'X'
        self.untill = 'X'
        self.basic = []
        self.extra = []

    def addAll(self):
        self.basic.append(self.untill)
        self.basic.append(self.company)
        self.basic.append(self.name)
        self.basic.append(self.rateWork)
        self.basic.append(self.salary)
        self.basic.append(self.recommend)
        self.basic.append(self.extra)

    def print(self):
        print(self.untill,self.company,self.name,self.rateWork,self.salary,self.recommend,self.extra)


def login(id, pwd):
    loginUrl = "https://www.jobplanet.co.kr/users/sign_in.html"
    br.session.headers.update({ 'User-agent':'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'})

    loginPage = br.get(loginUrl)

    loginForm = loginPage.soup.select("form")[1]

    loginForm.select("#user_email")[0]['value'] = id

    loginForm.select("#user_password")[0]['value'] = pwd

    page = br.submit(loginForm,loginPage.url)

    error = page.soup.findAll('span', attrs={'class':'error_txt'})

    if error:
        print("check your id(email) and password\m program is fail")
        sys.exit()

    return page


def get(lp, page = 3):

    url = "https://www.jobplanet.co.kr/job_postings/search.html?page="

    csv_file = open('jbplanet.csv', 'w')
    cw = csv.writer(csv_file, delimiter=',')

    page= page+1
    myObj = JobObject()
    for eachPage in range(1,page):
        print(str(eachPage)+"-----------")
        jp = br.get(url+str(eachPage))
        each = jp.soup.find_all(('div'), attrs={'class': 'result_unit_info'})


        for i in each:
            myObj.clear()
            try:

                if i.find('span').text != '' :
                    myObj.untill = i.find('span').text

                if i.find('p').text is not None:
                    myObj.company = i.find('p').text
                if i.find(attrs={'class':'posting_name'}) is not None:
                    myObj.name = i.find(attrs={'class':'posting_name'}).text
                if i.find(attrs={'class':'rate'}) is not None:
                    myObj.rateWork = i.find(attrs={'class':'rate'}).text
                if i.find(attrs={'class':'salary'}) is not None:
                    myObj.salary = i.find(attrs={'class':'salary'}).text
                if i.find(attrs={'class':'recommend'}) is not None:
                    myObj.recommend =i.find(attrs={'class':'recommend'}).text


                for j in i.findAll('span', attrs={'class':'tags'}):
                    myObj.extra.append(j.text)

                myObj.addAll()
                #myObj.print()
                cw.writerow(myObj.basic)

            except:
                print("except occur by incoding probleme")
                pass


    csv_file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get job information')
    parser.add_argument("page",help= "how many page you want it? less than 500",type=int)
    parser.add_argument("id", help = " your jobplanet ID")
    parser.add_argument("password", help= " your jobplanet pw")

    args = parser.parse_args()

    lp = login(args.id, args.password)
    get(lp, args.page)

