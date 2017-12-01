
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import csv
import codecs
from multiprocessing import Pool
import re
import time
import random

ua_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        ]

headers = {'User-agent': random.choice(ua_list)}

def my_soup(url):
    response = requests.get(url, headers=headers, timeout=8)
    bs = BeautifulSoup(response.text, 'lxml')
    return bs

def get_page(url):
    try:
        soup = my_soup(url)
        result_p = soup.find_all('p', class_='title')
        for p in result_p:
            page_text = str(p)
            page_detail = BeautifulSoup(page_text, 'lxml')
            href = page_detail.find_all('a')
            part_url = href[0].attrs['href']
            whole_url = 'http://esf.ks.fang.com%s' % part_url
            get_page_detail(whole_url)
        result_nextpage = soup.find_all('a', id='PageControl1_hlk_next')
        print(result_nextpage)
        if len(result_nextpage) != 0:
            next_url = 'http://esf.ks.fang.com%s' % result_nextpage[0].attrs['href']
            get_page(next_url)
        else:
            print('没有下一页了')
    except RequestException:
        return ('bad requests')

def my_strip(s):
    return str(s).replace(' ', '').replace('\n', '').replace('\t', '').strip()


def find_info(response):
    info = BeautifulSoup(str(response), 'lxml')
    detail = info.find_all('dd')
    return detail


def write_info(result):
    with codecs.open('房天下.csv', 'a', 'utf_8_sig') as f:
        writer = csv.writer(f)
        writer.writerow(result)
        f.close()

def get_url(quyu, m, a, b):
    url = 'https://ks.anjuke.com/sale/' + quyu + '/a' + str(a) + '-b' + str(b) + '-m' + str(m) + '/'
    return url

# 详细页面的爬取
def get_page_detail(url):
    try:
        soup = my_soup(url)
        result_list = []
        biaoti_line = soup.find_all('div', id='lpname')[0]
        #<div class="title" id="lpname">
        #世茂东外滩经典两房双阳台 88平毛坯置业首选 127万楼层佳            </div>
        title = my_strip(biaoti_line.text)
        jiage_line = str(soup.find_all('div', class_='trl-item sty1')[0])
        #<div class="trl-item sty1"><i>165</i>万</div>
        price = re.compile('\d+').findall(jiage_line)[1]
        items = soup.find_all('div', class_='trl-item1')
        items_soup = BeautifulSoup(str(items), 'lxml')
        items_2 = items_soup.find_all('div', class_='tt')
        #[<div class="tt">
        #2室1厅1卫        </div>, <div class="tt">84平米</div>, <div class="tt">14524元/平米</div>, <div class="tt">南北</div>, <div class="tt">中层</div>, <div class="tt">毛坯</div>]
        huxing = my_strip(items_2[0].text)
        mianji = my_strip(items_2[1].text[:-2])
        danjia = my_strip(items_2[2].text[:-4])
        chaoxiang = my_strip(items_2[3].text)
        louceng = my_strip(items_2[4].text)
        zhuangxiu = my_strip(items_2[5].text)
        xiaoqu_line = soup.find_all('a', title='查看此楼盘的更多二手房房源')
        #[<a class="blue" href="http://diehuwansm0512.fang.com/" id="agantesfxq_C03_05" style="text-decoration: underline;" target="_blank" title="查看此楼盘的更多二手房房源">世茂蝶湖湾</a>]
        xiaoqu = xiaoqu_line[0].text
        quyu_line = soup.find_all('div', id='address')
        quyu_soup = BeautifulSoup(str(quyu_line), 'lxml')
        quyu_2 = quyu_soup.find_all('a', class_='blue')
        #[ < a class ="blue" href="/house-a013260/" id="agantesfxq_C03_07" target="_blank" >
        #玉山
        #< / a >, < a class ="blue" href="/house-a013260-b04965/" id="agantesfxq_C03_08" target="_blank" >
        #城西
        #< / a >]
        quyu = my_strip(quyu_2[0].text) + my_strip(quyu_2[1].text)
        niandai = soup.find_all('span', class_='rcont')[0].text[:-1]
        result = [title, price, huxing, mianji, danjia, chaoxiang, louceng, zhuangxiu, xiaoqu, quyu, niandai]

        '''
        ['玉峰娄江星海花园精装修看房随时', '70', '1室1厅1卫', '44', '15909', '西', '低层', '精装修', '星海花园', '玉山城西', '2008']
        '''
        result_list.append(result)
        print(result)
        # with open('1.txt', 'a', encoding='UTF-8') as f:
        # f.write(str(result)+'\n')
        # f.close()
        write_info(result)
    except RequestException:
        return ('bad requests')


if __name__ == '__main__':
    start = time.clock()
    list = []
    for b in ('13260-b04964/', '13260-b04965/', '13260-b04961/', '13260-b04963/', '13260-b015734/', '13261-b014297/', '13261-b014295/',
              '13261-b014384/', '13261-b021901/', '13261-b021904/', '13263/', '13266/', '13262/', '13268/', '13267/', '13265/', '13264/', '13269/'):
        for cd in ('d250/', 'c250-d280/', 'c280-d2100/', 'c2100-d2120/', 'c2120-d2150/', 'c2150-d2200/', 'c2200-d2300/', 'c2300/'):
            url = 'http://esf.ks.fang.com/house-a0' + str(b) + str(cd)
            list.append(url)

    pool = Pool(20)
    pool.map(get_page, list)
    pool.close()
    pool.join()

    end = time.clock()
    print('程序运行时长为 %f 秒' % (end - start))















