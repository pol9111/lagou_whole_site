import asyncio
import aiohttp
import re
import time
from config import HEADERS, LAGOU_DONE, LAGOU_ITEMS, REDIS_CONN, LAGOU_BLANK, START_PAGE, LAGOU_RETRY, LAGOU_COOKIES
from saver import start_saver
from utils import get_cookie, start_save_cookie, take_proxy, get_proxy, update_proxy


async def fetch(sem, num, session):
    """下载器"""
    # proxy = eval(take_proxy())['https']
    base_url = 'https://www.lagou.com/jobs/{}.html'
    url = base_url.format(num)
    async with sem:
        try:
            # async with session.get(url, timeout=30, headers=HEADERS, proxy=proxy) as resp:
            async with session.get(url, timeout=30, headers=HEADERS) as resp:
                # print(proxy)
                print(resp.status, url)
                html = await resp.text()
                parse(html, num)
        except Exception:
            REDIS_CONN.sadd(LAGOU_RETRY, num)
            pass


async def downloader(ids, loop):
    """设置异步任务"""
    sem = asyncio.Semaphore(1024)
    tasks = []
    async with aiohttp.ClientSession(cookies=get_cookie(), loop=loop) as session:
        for num in ids:
            if REDIS_CONN.sismember(LAGOU_BLANK, num) or REDIS_CONN.sismember(LAGOU_DONE, num):
                pass
            else:
                task = asyncio.ensure_future(fetch(sem, num, session))
                tasks.append(task)
        await asyncio.gather(*tasks)


def parse(html, num):
    """解析页面"""
    blank = re.findall(r'<div class="content">(.*?)<a href="https://www.lagou.com/">回首页</a>', html, re.S)
    if blank:
        REDIS_CONN.sadd(LAGOU_BLANK, num)
    else:
        position = re.findall(r'<span class="name">(.*?)</span>', html)[0]
        company = re.findall(r'<h2 class="fl">(.*?)<i', html, re.S)[0].strip()
        publish_time = re.findall(r'<p class="publish_time">(.*?)&nbsp;', html, re.S)[0]
        info = re.findall(r'<dd class="job_request">.*?<p>(.*?)</p>', html, re.S)[0]
        info_list = re.findall(r'>(.*?)</span>', info)
        salary = info_list[0].replace(' ', '')
        city = info_list[1].replace(' ', '').replace('/', '')
        experience = info_list[2].replace(' ', '').replace('/', '')
        edu = info_list[3].replace(' ', '').replace('/', '')
        work_time = info_list[4]
        addr_ = re.findall(r'bizArea=.*?#filterBox">.*?</a>(.*?)<a rel="nofollow" href="javascript:;" id="mapPreview">查看地图</a>',
                           html, re.S)
        if addr_:
            addr = addr_[0].replace(' ', '').replace('\n', '').replace('-', '')
        else:
            addr = ''

        data = {
            'id': num,
            'position': position,
            'company': company,
            'salary': salary,
            'city': city,
            'experience': experience,
            'edu': edu,
            'work_time': work_time,
            'publish_time': publish_time,
            'addr': addr,
        }
        print(data)
        save_to_redis(data, num)


def save_to_redis(data, num):
    """暂存redis"""
    if data:
        REDIS_CONN.lpush(LAGOU_ITEMS, str(data))
        REDIS_CONN.sadd(LAGOU_DONE, num)


def start_requests(urls, loop):
    """开始请求任务"""
    loop.run_until_complete(downloader(urls, loop))


def start_retry(loop):
    """开始爬取重试队列"""
    while REDIS_CONN.scard(LAGOU_RETRY) > 500:
        print('开始重试队列下一循环..')
        retry_list = []
        for _ in range(500):
            movie_id = REDIS_CONN.spop(LAGOU_RETRY)
            retry_list.append(movie_id)
        start_requests(retry_list, loop)
        check_and_save(loop)

    retry_list = []
    for _ in range(REDIS_CONN.scard(LAGOU_RETRY)):
        movie_id = REDIS_CONN.spop(LAGOU_RETRY)
        retry_list.append(movie_id)
    start_requests(retry_list, loop)
    check_and_save(loop)
    loop.close()
    print('FINISH!!')


def check_and_save(loop):
    """检查代理可用性, 数据持久化"""
    check = REDIS_CONN.llen(LAGOU_ITEMS)
    if check < 1:
        print('代理可用度低, 正在更换代理..')
        # update_proxy()
        REDIS_CONN.delete(LAGOU_COOKIES)
        start_save_cookie()
    if check:
        start_saver(loop)


def main():
    # get_proxy()
    start_save_cookie()
    loop = asyncio.get_event_loop()
    for index in range(START_PAGE, 5000000, 500):
        print('开始下一循环..', index)
        page = [num for num in range(index, index+500)]
        start_requests(page, loop)
        check_and_save(loop)
        print('等待片刻..')
        time.sleep(3)

    start_retry(loop)


if __name__ == '__main__':
    main()