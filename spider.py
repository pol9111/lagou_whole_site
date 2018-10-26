import asyncio
import aiohttp
import re
import time
from config import HEADERS, LAGOU_DONE, LAGOU_ITEMS, REDIS_CONN, LAGOU_BLANK, START_PAGE, LAGOU_RETRY, LAGOU_COOKIES, PER_LOOP
from saver import save_handler
from utils import cookie_handler, proxy_handler


class LagouSpider(object):

    def __init__(self):
        self.headers = HEADERS
        self.lagou_done = LAGOU_DONE
        self.lagou_items = LAGOU_ITEMS
        self.redis_conn = REDIS_CONN
        self.lagou_blank = LAGOU_BLANK
        self.start_page = START_PAGE
        self.lagou_retry = LAGOU_RETRY
        self.lagou_cookies = LAGOU_COOKIES
        self.per_loop = PER_LOOP

    async def fetch(self, sem, num, session):
        """下载器"""
        # proxy = eval(proxy_handler.take_proxy())['https']
        base_url = 'https://www.lagou.com/jobs/{}.html'
        url = base_url.format(num)
        async with sem:
            try:
                # async with session.get(url, timeout=30, headers=self.headers, proxy=proxy) as resp:
                async with session.get(url, timeout=30, headers=self.headers) as resp:
                    # print(proxy)
                    print(resp.status, url)
                    html = await resp.text()
                    self.parse(html, num)
            except Exception:
                self.redis_conn.sadd(self.lagou_retry, num)
                pass


    async def downloader(self, ids, loop):
        """设置异步任务"""
        sem = asyncio.Semaphore(1024)
        tasks = []
        async with aiohttp.ClientSession(cookies=cookie_handler.get_cookie(), loop=loop) as session:
            for num in ids:
                if self.redis_conn.sismember(self.lagou_blank, num) or self.redis_conn.sismember(self.lagou_done, num):
                    pass
                else:
                    task = asyncio.ensure_future(self.fetch(sem, num, session))
                    tasks.append(task)
            await asyncio.gather(*tasks)


    def parse(self, html, num):
        """解析页面"""
        blank = re.findall(r'<div class="content">(.*?)<a href="https://www.lagou.com/">回首页</a>', html, re.S)
        if blank:
            self.redis_conn.sadd(self.lagou_blank, num)
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
            self.save_to_redis(data, num)


    def save_to_redis(self, data, num):
        """暂存redis"""
        if data:
            self.redis_conn.lpush(self.lagou_items, str(data))
            self.redis_conn.sadd(self.lagou_done, num)


    def start_requests(self, urls, loop):
        """开始请求任务"""
        loop.run_until_complete(self.downloader(urls, loop))


    def start_retry(self, loop):
        """开始爬取重试队列"""
        while self.redis_conn.scard(self.lagou_retry) > self.per_loop:
            print('开始重试队列下一循环..')
            retry_list = []
            for _ in range(self.per_loop):
                movie_id = self.redis_conn.spop(self.lagou_retry)
                retry_list.append(movie_id)
            self.start_requests(retry_list, loop)
            self.check_and_save(loop)

        retry_list = []
        for _ in range(self.redis_conn.scard(self.lagou_retry)):
            movie_id = self.redis_conn.spop(self.lagou_retry)
            retry_list.append(movie_id)
        self.start_requests(retry_list, loop)
        self.check_and_save(loop)
        loop.close()
        print('FINISH!!')


    def check_and_save(self, loop):
        """检查代理可用性, 数据持久化"""
        check = self.redis_conn.llen(self.lagou_items)
        if check < 1:
            print('代理可用度低, 正在更换代理..')
            # proxy_handler.update_proxy()
            self.redis_conn.delete(self.lagou_cookies)
            cookie_handler.start_save_cookie()
        if check:
            save_handler.start_saver(loop)


    def main(self):
        # proxy_handler.get_proxy()
        cookie_handler.start_save_cookie()
        loop = asyncio.get_event_loop()
        for index in range(self.start_page, 5000000, self.per_loop):
            print('开始下一循环..', index)
            page = [num for num in range(index, index+self.per_loop)]
            self.start_requests(page, loop)
            self.check_and_save(loop)
            print('等待片刻..')
            time.sleep(3)
        self.start_retry(loop)


if __name__ == '__main__':
    LagouClawer = LagouSpider()
    LagouClawer.main()