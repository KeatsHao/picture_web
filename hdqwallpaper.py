import requests
import re
import json
import time
from requests.exceptions import RequestException
from selenium import webdriver
from pyquery import PyQuery as pq
import csv
import os
import gc
import argparse

def get_one_page(url,referer):      #得到页面源码
    try:
        headers={
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            'Cookie':'__cfduid=d3eb292ff11fef9392a636f16c4659fa31589971494; _ga=GA1.2.1573046522.1589971498; __gads=ID=228be6ab2ea6194d:T=1589971499:S=ALNI_MYUcnFcPs07xpdgwGTbvvb4ME399A; _gid=GA1.2.602702836.1590560338; PHPSESSID=810d70856bf1a37ed1963f31c59941cc',
            'referer':referer,
            }
        response=requests.get(url,headers=headers)
        if response.status_code==200:
            return response.text            #txt改成了text
        return None
    except RequestException:
        return None

def get_total_page_number_data(html):       #提取最大页数
    if html==None:
        return print('——————没有得到主页正确源代码——————')
    pattern=re.compile("\d+(?=</a></li><li class=''><a id='next' href)")        #正向先行断言
    item=re.findall(pattern,html)
    return int(item[0])

def parse_one_page(html):       #提取主页信息
    if html==None:
        return print('——————没有得到主页正确源代码——————')
    pattern=re.compile('<div class=\'wall-resp col-lg-4 col-md-4 col-sm-4 col-xs-6 column_padding\'><a href=\'(.*?)\' class=\'caption hidden-md hidden-sm hidden-xs\' style=\'z-index:1\' title=\''
                       +'(.*?)\'>(.*?)</a><a href=')
    items=re.findall(pattern,html)
    for item in items:
        yield {'item_url':item[0],'item_id':item[2]}

def parse_one_page_sub(html):       #提取子页信息
    if html==None:
        return print('——————没有得到子页正确源代码——————')
    pattern='</a> \| Author :\n<a href="(.*?)" target="_blank" class="btn-link btn-link_a"><i> (.*?)</i></a> </footer>'
    item=re.findall(pattern,html)
    author=item[0][1]
    author_url=item[0][0]
    pattern=' <a href="(.*?)" rel="nofollow" class="btn btn-fresh btn-default-res" style="border-radius:10px;" target="_blank">Download Original'
    item=re.findall(pattern,html)
    img_url=item[0]
    return author_url,author,img_url

def save_to_csv(list_2d,doc):       #保存文件
    with open(doc,'a',newline='') as f:
        writer=csv.writer(f)
        if not os.path.getsize(doc):
            writer.writerow(['image_name','image_url','author','author_url'])
        writer.writerows(list_2d)
        print('******写入成功')


def deal_one_page(num,list_2d=[],tag=0,search_key='scifi'):        #对每个分页求其中每个照片的地址或者判断num求总页数
    url_base='https://hdqwalls.com/'       
    url_connect='search?q='
    search_page='&page=%d'%num
    url=url_base+url_connect+search_key+search_page
    if tag==1:
        html_content=get_one_page(url,url_base)
        item=get_total_page_number_data(html_content)
        return item
    html_content=get_one_page(url,url_base)
    for item in parse_one_page(html_content):
        print(item)
        url_sub=url_base+item['item_url']
        #options=webdriver.ChromeOptions()
        #options.add_argument('--headless')
        browser=webdriver.Chrome()
        browser.get(url_sub)
        html_sub_content=browser.page_source
        author_url,author,img_url=parse_one_page_sub(html_sub_content)
        browser.close()
        list_2d.append([item['item_id'],img_url,author,author_url])


def web_parser():
    parser=argparse.ArgumentParser(description='下载图片信息')
    parser.add_argument('--target',type=str,help='Type of pictures you want.')     #爬取的关键字
    parser.add_argument('--doc',type=str,help='File you create to store the information.')        #保存图片信息的文件
    return parser.parse_args().target,parser.parse_args().doc


def main():
    #category,doc=web_parser()
    number=0
    while True:
        if number==0:       #第一次寻找此次任务的总页数也就是总循环
            number+=1
            tag=1           #tag标识是否是查找总页数
            MAX=deal_one_page(number,tag=1)
            print('max_number is ',MAX)
        info=list()
        deal_one_page(num=number,list_2d=info)
        save_to_csv(info,doc)           #在此处进行io，降低开销,增加容错
        del info
        gc.collect()
        number+=1
        if number>MAX:
            return print('***********   Congratulations !!  Task is over !!')


if __name__=='__main__':
    main() 
