# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import json
import logging
import requests

KEYWORDS = [u'科技', u'创新', u'人才', u'科创', u'科学', u'产业园', u'创业基地', u'大数据', u'智能', u'研发']

def get_article(url, date):
    #logging.info('GET {}'.format(url))
    ok = False
    while not ok:
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            logging.error('Encountered ConnectionError, retrying: {}'.format(str(e)))
        else:
            ok = True
    r.encoding = 'utf-8'
    if 'Sorry, Page Not Found' in r.text:
        logging.info('Article not found')
        return False, None
    soup = BeautifulSoup(r.text, 'html.parser')
    #logging.info('GET OK')
    content = soup.find('founder-content')
    title = soup.find('founder-title')
    author = soup.find('founder-author')
    result = {}
    result['url'] = url
    result['title'] = title.text.replace('\n', '')
    result['date'] = str(date)
    result['author'] = author.text.replace('\n', '')
    has_keyword, keywords = check_keyword(content.text)
    result['keywords'] = keywords
    result['text'] = content.text
    logging.info('title: {}, date: {}, has keywords: {}'.format(result['title'], result['date'], has_keyword))
    return has_keyword, result

def check_keyword(text):
    has_keyword = False 
    included_keywords = ''
    for kw in KEYWORDS:
        if kw in text:
            has_keyword = True
            included_keywords += kw + '|'
    return has_keyword, included_keywords

def scrape_issue(date, runid):
    month = '0' + str(date.month) if len(str(date.month)) == 1 else str(date.month)
    day = '0' + str(date.day) if len(str(date.day)) == 1 else str(date.day)
    url = 'http://epaper.jrkunshan.cn/html/{0}-{1}/{2}/index_{0}-{1}-{2}.htm'.format(date.year, month, day)
    print(url)
    logging.info('GET {}'.format(url))
    r = requests.get(url)
    r.encoding = 'utf-8'
    if 'Sorry, Page Not Found' in r.text:
        logging.info('Issue not found')
        return
    soup = BeautifulSoup(r.text, 'html.parser')
    # get urls of all articles of the issue
    logging.info('GET OK, traversing articles')
    articles = soup.find_all('a', href=True)
    for a in articles:
        if 'content' in a['href'] and u'广告' not in a.text and u'公告' not in a.text:   
            a_url = 'http://epaper.jrkunshan.cn/html/{0}-{1}/{2}/{3}'.format(date.year, month, day, a['href'])
            has_keyword, result = get_article(a_url, date)
            if has_keyword:
                result['run'] = runid
                filename = str(date) + a['href'] + '.json'
                logging.info('Dumping json to {}'.format(filename))
                with open('data/'+filename, 'w') as f:
                    json.dump(result, f)
                    f.close()
                #print(result)

def main(begin_date, end_date=date(2009, 5, 1)):
    now = datetime.now()
    runid = hash(now)
    logging.basicConfig(filename='{}.log'.format(runid), 
    format='%(asctime)s %(funcName)s %(levelname)s:%(message)s', 
    filemode='w', 
    level=logging.INFO)
    logging.info('Begin time: {}, run id: {}'.format(now, runid))
    logging.info('Begin scraping on {} and ending on {}'.format(begin_date, end_date))
    one_day = timedelta(days=1)
    curr_date = begin_date
    # starts scraping each issue starting from begin date
    while curr_date >= end_date:
        logging.info('Scrapping on issue {}'.format(curr_date))
        scrape_issue(curr_date, runid)
        # print(curr_date)
        curr_date -= one_day
    logging.info('Scrapping completed')

# get_article('http://epaper.jrkunshan.cn/html/2019-05/31/content_5_1.htm')
# 'http://epaper.jrkunshan.cn/html/2019-04/11/content_4_7.htm'
#  http://epaper.jrkunshan.cn/html/2019-06/18/content_1_3.htm
#  http://epaper.jrkunshan.cn/html/2019-06/04/content_1_2.htm

# scrape_issue(date(2019, 6, 7))
# main(date(2019, 6, 7))

# main(date(2019, 6, 8))

if __name__ == '__main__':
    begin_date = input('Begin date: ')
    begin_date = datetime.strptime(begin_date, '%Y-%m-%d')
    begin_date = begin_date.date()
    end_date = input('End date: ')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    end_date = end_date.date()
    #print(begin_date, end_date)
    main(begin_date, end_date)