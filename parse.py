# -*- coding: UTF-8 -*-

import json
import os
import pandas as pd
import sqlite3

def to_sql():
    """
    Write the json files into a sql db.
    """
    conn = sqlite3.connect('kunshan')
    c = conn.cursor()
    jsons = os.listdir('data/')
    jsons = list(filter(lambda f: '.json'==f[-5:], jsons))
    num_files = len(jsons)
    print('Detected {} json files under data/, reading...'.format(num_files))
    #print(jsons)
    results = []
    count = 0
    for j in jsons:
        with open('data/'+j, 'r') as f:
            result = json.load(f)
            f.close()
        count += 1
        if count % 1000 == 0:
            print('Read {} of {}'.format(count, num_files))
        #print(result)
        results.append((result['url'], result['title'], result['date'], result['author'], result['keywords']))
    
    print('Executing bulk inserts...')
    c.executemany('INSERT INTO article VALUES (?, ?, ?, ?, ?)', results)
    conn.commit()
    conn.close()
    print('SQL write complete')

def to_excel():
    """
    Read from sql db and write the results to a excel file.
    """
    conn = sqlite3.connect('kunshan')
    query = 'SELECT url, title, date, author, keywords FROM main.article'
    print('Reading from DB...')
    kunshan = pd.read_sql(query, conn, parse_dates=['date'])
    print('done')
    kunshan['num_keywords'] = kunshan.apply(lambda r: r['keywords'].count('|'), axis=1)
    kunshan = kunshan[kunshan['num_keywords']>1] # filter out entries with only 1 keyword included
    kunshan = kunshan[['date', 'keywords', 'num_keywords', 'title', 'url', 'author']]
    kunshan['date'] = kunshan['date'].dt.date
    kunshan.columns = [u'日期', u'包含关键词', u'关键词数量', u'主题', u'链接', u'作者']
    #print(kunshan)
    conn.close()
    print('Writing to Excel...')
    kunshan.to_excel(u'汇总.xlsx', na_rep='NA', index=False)
    print('done')

if __name__ == "__main__":
    option = input('SQL: 1 \nExcel: 2 > ')
    if option == '1':
        to_sql()
    elif option == '2':
        to_excel()
