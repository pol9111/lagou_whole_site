import random
from selenium import webdriver
from config import REDIS_CONN, LAGOU_COOKIES


def save_cookie():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument("--proxy-server=http://202.20.16.82:10152")
    browser = webdriver.Chrome(chrome_options=chrome_options)
    page = random.randint(100, 999)
    url = f'https://www.lagou.com/jobs/4939{str(page)}.html'
    browser.get(url)
    cookie_items = browser.get_cookies()
    cookies = {}
    for cookie_item in cookie_items:
        cookies[cookie_item['name']] = cookie_item['value']
    REDIS_CONN.lpush(LAGOU_COOKIES, cookies)


def start_save_cookie():
    for _ in range(5):
        save_cookie()


def get_cookie():
    all_cookies = REDIS_CONN.lrange(LAGOU_COOKIES, 0, -1)
    # return all_cookies
    cookies = eval(random.choice(all_cookies))
    print(cookies)
    return cookies


# start_save_cookie()