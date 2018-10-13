from selenium import webdriver
from config import REDIS_CONN, PROIES, PROXY_URL, LAGOU_COOKIES
import requests
import random


def save_cookie(browser):
    page = random.randint(10000, 99999)
    url = f'https://www.lagou.com/jobs/49{str(page)}.html'
    try:
        browser.get(url)
        cookie_items = browser.get_cookies()
        cookies = {}
        for cookie_item in cookie_items:
            cookies[cookie_item['name']] = cookie_item['value']
        if cookies:
            REDIS_CONN.lpush(LAGOU_COOKIES, cookies)
            print('已获取一个cookies')
        else:
            print('获取cookies失败')
    except Exception:
        pass


def start_save_cookie():
    print('开始获取cookies')
    # proxy = eval(get_proxy())['https']
    # print(proxy)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument("--proxy-server={}".format(proxy))
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.set_page_load_timeout(40)
    for _ in range(5):
        save_cookie(browser)
    try:
        browser.close()
    except:
        pass
    if REDIS_CONN.llen(LAGOU_COOKIES) < 5:
        start_save_cookie()


def get_cookie():
    if REDIS_CONN.llen(LAGOU_COOKIES):
        all_cookies = REDIS_CONN.lrange(LAGOU_COOKIES, 0, -1)
        cookies = eval(random.choice(all_cookies))
        return cookies
    else:
        start_save_cookie()


def get_proxy():
    html = requests.get(PROXY_URL).json()
    ips = html.get('msg')
    for dic in ips:
        ip = dic.get('ip')
        port = dic.get('port')
        ip_port = {'https': 'http://' + ip + ':' + port}
        REDIS_CONN.lpush(PROIES, ip_port)


def take_proxy():
    proxy_list = REDIS_CONN.lrange(PROIES, 0, -1)
    proxy = random.choice(proxy_list)
    return proxy


def update_proxy():
    REDIS_CONN.delete(PROIES)
    get_proxy()