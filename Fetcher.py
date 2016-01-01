import os
import re
import sys
import html
import time
import random
import hashlib
import os.path
import logging
import selenium
import requests
import datetime  
import PyRSS2Gen
import HTMLParser
import urllib.request
from bs4 import BeautifulSoup  
from selenium import webdriver
from urllib.parse import quote
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

ISOTIMEFORMAT='%Y-%m-%d %X'
BASE_URL = 'http://weixin.sogou.com'
EXT = ''
UA = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
LOG_PATH="D://websites//tw_wordpress//cronlog.txt"
XML_PATH="D://websites//tw_wordpress//twrss.xml"
REAL_HREF=""
IMG_PATH="D://websites//tw_wordpress//wximg"

def get_html(url):
    #chromedriver = 'C:/Users/_/AppData/Local/Google/Chrome/Application/chromedriver.exe'
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        UA
    )
    dcap["takesScreenshot"] = (False)
    try:
        
        options = webdriver.ChromeOptions()
        options.add_argument(UA) 
        browser.get(url + '&ext=' + EXT)
        browser.implicitly_wait(30)
        time.sleep(1)
        #智能等待30秒
        WebDriverWait(browser, 10).until(lambda browser : browser.find_element_by_css_selector('#wxmore > a'))
        element=WebDriverWait(browser, 10).until(lambda browser : browser.find_element_by_css_selector('#wxmore > a'))
        element.click()
        time.sleep(1)
    except selenium.common.exceptions.WebDriverException:
       pass
    try:
        html = browser.page_source
    except Exception as e:
        html = None
        logging.error(e)
    return html

def get_ehtml(url):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        UA
    )
    dcap["takesScreenshot"] = (False)
    #t0 = time.time()
    try:
        options = webdriver.ChromeOptions()
        options.add_argument(UA) 
        browser.get(url + '&ext=' + EXT)
        WebDriverWait(browser, 10).until(lambda browser : browser.find_element_by_css_selector('#page-content'))
        time.sleep(1)
    except selenium.common.exceptions.WebDriverException:
       pass
    try:
        html = browser.page_source
        global REAL_HREF
        REAL_HREF = browser.current_url
    except Exception as e:
        html = None
        logging.error(e)
    return html

def get_dhtml(url):
    #chromedriver = 'C:/Users/_/AppData/Local/Google/Chrome/Application/chromedriver.exe'
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (UA)
    dcap["takesScreenshot"] = (False)
    #t0 = time.time()
    try:
        options = webdriver.ChromeOptions()
        options.add_argument(UA) 
        browser.get(url)
        browser.implicitly_wait(2)
    except selenium.common.exceptions.WebDriverException:
       pass
    try:
        html = browser.page_source
    except Exception as e:
        html = None
        logging.error(e)
    return html

def get_html_direct(url,cookies=None):
    if not cookies:
        cookies = update_cookies()
    headers = {"User-Agent": UA}
    r = requests.get(url, headers=headers, cookies=cookies, timeout=20)
    r.encoding='utf8'  
    return r.text
    
def parse_essay(link):
        e = get_ehtml(link)
        html = e
        soup = BeautifulSoup(html,"html.parser")
        essay = {}
        p = re.compile(r'\?wx_fmt.+?\"')
        d = re.compile(r'data-wxsrc="data.image.png.base64.\S*"')
        b = soup.select("#js_content")[0]
        content = str(b).replace('src', 'data-wxsrc')
        content = content.replace('data-data-wxsrc', 'src')
        content = re.sub(p, '"', content)
        content = re.sub(d, '', content)
        pic_Soup = BeautifulSoup(content,"html.parser")
        pic_pool = pic_Soup.find_all('img')
        try:
            for pic in pic_pool:
                link = pic.get('src')
                try:
                    filename = link.replace('/','').replace('\\','')+'.jpg'
                except:
                    filename = link + '.jpg'
                filename = filename[-15:]
                if not os.path.exists(IMG_PATH+'//'+filename):
                    urllib.request.urlretrieve(link,IMG_PATH+'//'+filename)
                content = content.replace(link,"http://127.0.0.1/wximg/"+filename)
        except:
            pass
        essay['content'] =content
        essay['name'] = soup.select('#post-user')[0].text
        essay['date'] = soup.select('#post-date')[0].text
        return essay

   
def get_account_info(open_id=None, link=None, cookies=None):
    url = None
    if open_id:
        url = BASE_URL + '/gzh?openid=' + open_id
    if link:
        url = link
    #html = get_html(url)
    #html = get_html_direct(url, cookies=cookies)
    html = get_dhtml(url)
    #print(html)
    if not html:
        return None
    soup = BeautifulSoup(html,"html.parser")
    try:
        info_box = soup.select('#weixinname')[0].parent
    except:  
        fp.write("\n达到搜狗限制，结束任务")
        fp.close()
        exit('OUT OF TODAY RANGE!')
    account_info = {}
    account_info['account'] = info_box.select('h4 span')[0].text.split('：')[1].strip()
    account_info['name'] = info_box.select('#weixinname')[0].text
    account_info['address'] = url
    account_info['description'] = info_box.select('.sp-txt')[0].text
    img_list = soup.select('.pos-box img')
    account_info['logo'] = soup.select(".img-box img")[0]['src']
    global  rss
    rss=PyRSS2Gen.RSS2(
                          title=account_info['name'],
                          link="/" + get_md5_value(str(account_info['name']).encode("utf8")),
                          description = account_info['description'],
                          pubDate = account_info['description'],
                          items=[]
                          );
    return account_info
def get_md5_value(src):
    myMd5 = hashlib.md5()
    myMd5.update(src)
    myMd5_Digest = myMd5.hexdigest()
    return myMd5_Digest
def parse_list(open_id=None, link=None):
    if open_id:
        url = BASE_URL + '/gzh?openid=' + open_id
    elif link:
        url = link
    else:
        return None
    html = get_html(url)
    if not html:
        return None
    soup = BeautifulSoup(html,"html.parser")
    ls = soup.select('#wxbox .txt-box')
    link_list = []
    num = len(ls)
    pnum = 1
    print('Got:'+str(num))
    fp.write("\nGot:"+str(num)+"||")
    for item in ls:
        print('Process:'+str(pnum))
        essay = parse_essay(BASE_URL + item.a['href'])
        rss.items.append(PyRSS2Gen.RSSItem(  
         title = item.a.text,  
         link = "/" + get_md5_value(str(item.a.text).encode("utf8")),  
         description = essay['content'],  
         pubDate = essay['date'])); 
        item_dict = {}
        item_dict['title'] = item.a.text
        item_dict['link'] = item.a['href']
        if (pnum) == num:
            fp.write("LastOne")
        else:
            if (pnum) == 1:
                fp.write(item.a.text + "(" + str(essay['date']) +")-")    
            else:
                fp.write(str(pnum)+"-")
        pnum+=1
    fp.write("\nSaveXml")
    try:
        rss.write_xml(open(XML_PATH, "w",encoding='utf-8'))
    except:
        fp.write(".....Failed!")
    else:
        fp.write(".....Done!")
        

def weixin_search(name, cookies=None):
    url = BASE_URL + '/weixin?query=' + name
    #html = get_html(url)
    html = get_html_direct(url, cookies=cookies)
    soup = BeautifulSoup(html,"html.parser")
    ls = soup.select("._item")
    search_list = []
    for item in ls:
        account_info = {}
        account_info['account'] = item.select('h4 span')[0].text.split('：')[1].strip()
        account_info['name'] = item.select('.txt-box h3')[0].text
        if account_info['name'] == name:
            tmp_ext = item['href'].split('ext=')[1]
            try:
                return str(tmp_ext)
            except:
                fname =  str(int(time.time()))
                browser.save_screenshot(fname+".png")
                fp.write("\n获取EXT参数出错，截图为:"+fname+".png");
                exit('Error On Fetch EXT')

def update_cookies():
    s = requests.Session()
    s.cookies.clear()
    s.cookies.clear_session_cookies()
    headers = {"User-Agent": UA}
    s.headers.update(headers)
    url = BASE_URL + '/weixin?query=123'
    r = s.get(url)
    if 'SNUID' not in s.cookies:
        p = re.compile(r'(?<=SNUID=)\w+')
        s.cookies['SNUID'] = p.findall(r.text)[0]
        suv = ''.join([str(int(time.time()*10000) + random.randint(0, 1000))])
        s.cookies['SUV'] = suv
    return s.cookies
    
    
if __name__ == '__main__':
    global fp
    fp = open(LOG_PATH,"a",encoding='utf-8') #打开一个文本文件
    fp.write("\n------------------------------------")
    fp.write("\n任务启动：\n任务类型:创建RSS文件\n时间:" + time.strftime( ISOTIMEFORMAT, time.localtime()))
    phantomJSdriver =sys.path[0] + '/bin/phantomjs.exe'
    global browser
    #browser = webdriver.Chrome(chromedriver)
    browser = webdriver.PhantomJS(phantomJSdriver)
    browser.delete_all_cookies() 
    try:
        open_id = 'oIWsFtzTQD0avasLckjN1Yz0bqW4'
        fp.write("\nopenid ="+open_id);
        cookies = update_cookies()
        fp.write("\n"+str(get_account_info(open_id,cookies=cookies)));
        EXT = weixin_search("湖理青年",cookies)
        fp.write("\next="+EXT)
        parse_list(open_id)
        fp.write("\n任务成功完成。")
    finally:
        fp.close()
        browser.quit()