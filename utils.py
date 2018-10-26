from selenium import webdriver
from config import REDIS_CONN, PROIES, PROXY_URL, LAGOU_COOKIES
import requests
import random


class CookieHandler(object):

    def __init__(self):
        self.redis_conn = REDIS_CONN
        self.lagou_cookies = LAGOU_COOKIES

    def save_cookie(self, browser):
        page = random.randint(10000, 99999)
        url = f'https://www.lagou.com/jobs/49{str(page)}.html'
        try:
            browser.get(url)
            cookie_items = browser.get_cookies()
            cookies = {}
            for cookie_item in cookie_items:
                cookies[cookie_item['name']] = cookie_item['value']
            if cookies:
                self.redis_conn.lpush(self.lagou_cookies, cookies)
                print('已获取一个cookies')
            else:
                print('获取cookies失败')
        except Exception:
            pass

    def start_save_cookie(self):
        print('开始获取cookies')
        # proxy = eval(get_proxy())['https']
        # print(proxy)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        # chrome_options.add_argument("--proxy-server={}".format(proxy))
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.set_page_load_timeout(40)
        for _ in range(5):
            self.save_cookie(browser)
        try:
            browser.close()
        except:
            pass
        if self.redis_conn.llen(self.lagou_cookies ) < 5:
            self.start_save_cookie()

    def get_cookie(self):
        if self.redis_conn.llen(self.lagou_cookies ):
            all_cookies = self.redis_conn.lrange(self.lagou_cookies , 0, -1)
            cookies = eval(random.choice(all_cookies))
            return cookies
        else:
            self.start_save_cookie()


class ProxyHandler(object):

    def __init__(self):
        self.redis_conn = REDIS_CONN
        self.proies = PROIES
        self.proxy_url = PROXY_URL

    def get_proxy(self):
        html = requests.get(self.proxy_url).json()
        ips = html.get('msg')
        for dic in ips:
            ip = dic.get('ip')
            port = dic.get('port')
            ip_port = {'https': 'http://' + ip + ':' + port}
            self.redis_conn.lpush(self.proies, ip_port)

    def take_proxy(self):
        proxy_list = self.redis_conn.lrange(self.proies, 0, -1)
        proxy = random.choice(proxy_list)
        return proxy

    def update_proxy(self):
        self.redis_conn.delete(self.proies)
        self.get_proxy()


cookie_handler = CookieHandler()
proxy_handler = ProxyHandler()