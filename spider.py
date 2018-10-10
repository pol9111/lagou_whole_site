import asyncio
import random
import re
import aiohttp
import aioredis
from config import HEADERS, LAGOU_DONE, LAGOU_ITEMS
from cookies_pool import get_cookie


def get_proxy():
    arr = [
        {'https': 'http://89.232.37.103:8080'},
        {'https': 'http://83.68.37.99:37796'},
        {'https': 'http://79.142.118.250:33691'},
        {'https': 'http://45.221.73.10:34831'},
    ]
    proxy = random.choice(arr)
    return proxy


async def fetch(sem, num, session):
    """下载器"""
    proxy = get_proxy()['https']
    base_url = 'https://www.lagou.com/jobs/{}.html'
    url = base_url.format(num)
    async with sem:
        async with session.get(url, timeout=10, headers=HEADERS) as resp:
            print(proxy)
            print(resp.status, url)
            html = await resp.text()
            await parse(html, num)



async def downloader(ids):
    """设置异步任务"""
    sem = asyncio.Semaphore(1024)
    tasks = []
    async with aiohttp.ClientSession(cookies=get_cookie()) as session:
        for num in ids:
            task = asyncio.ensure_future(fetch(sem, num, session))
            tasks.append(task)
        await asyncio.gather(*tasks)



async def parse(html, num):
    """解析页面"""
    blank = re.findall(r'<div class="content">(.*?)<a href="https://www.lagou.com/">回首页</a>', html, re.S)
    if blank:
        del num
    else:
        position = re.findall(r'<span class="name">(.*?)</span>', html)[0]
        company = re.findall(r'<h2 class="fl">(.*?)<i', html, re.S)[0].strip()
        publish_time = re.findall(r'<p class="publish_time">(.*?)&nbsp;', html, re.S)[0]
        addr = re.findall(r'bizArea=.*?#filterBox">.*?</a>(.*?)<a rel="nofollow" href="javascript:;" id="mapPreview">查看地图</a>',
                          html, re.S)[0].replace(' ', '').replace('\n', '').replace('-', '')
        info = re.findall(r'<dd class="job_request">.*?<p>(.*?)</p>', html, re.S)[0]
        info_list = re.findall(r'>(.*?)</span>', info)
        salary = info_list[0].replace(' ', '')
        city = info_list[1].replace(' ', '').replace('/', '')
        experience = info_list[2].replace(' ', '').replace('/', '')
        edu = info_list[3].replace(' ', '').replace('/', '')
        work_time = info_list[4]

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
        await save_to_redis(data)


async def save_to_redis(data):
    """暂存redis"""
    redis = await aioredis.create_redis_pool(
        'redis://localhost', minsize=5, maxsize=10, loop=loop)
    await redis.lpush(LAGOU_ITEMS, str(data))
    redis.close()
    await redis.wait_closed()



loop = asyncio.get_event_loop()
page = list(range(5201856, 5201857))
loop.run_until_complete(downloader(page))
loop.close()