# import random
# import asyncio
# import aiohttp
# from fake_useragent import UserAgent
# from cookies_pool import get_cookie
#
#
#
# headers = {
# 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
# 'Accept-Encoding': 'gzip, deflate, br',
# 'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
# 'Cache-Control': 'no-cache',
# 'Connection': 'keep-alive',
# 'Host': 'www.lagou.com',
# 'Pragma': 'no-cache',
# # 'Referer': url,
# 'Upgrade-Insecure-Requests': '1',
# 'User-Agent': UserAgent().random,
# }
#
#
#
#
# def get_proxy():
#     arr = [
#         {'https': 'http://47.105.151.103:80'},
#         # {'https': 'http://218.60.8.98:3129'},
#         # {'https': 'http://91.106.29.37:60582'},
#         # {'https': 'http://89.232.34.169:8080'},
#     ]
#     proxy = random.choice(arr)
#     return proxy
#
#
# async def fetch(sem, num, session):
#     """下载器"""
#     proxy = get_proxy()['https']
#     base_url = 'https://www.lagou.com/jobs/{}.html'
#     url = base_url.format(num)
#     async with sem: # 限制最大操作
#         async with session.get(url, timeout=10, headers=headers) as resp: # 发送请求
#             print(proxy)
#             print(resp.status, url)
#             html = await resp.text()
#             print(html)
#             return html
#
#
# async def downloader(ids):
#     """设置异步任务"""
#     sem = asyncio.Semaphore(1024)  # 设置最大操作
#     tasks = []
#     async with aiohttp.ClientSession(cookies=get_cookie()) as session:  # 创建可复用的会话减少开销
#         for num in ids:
#             task = asyncio.ensure_future(fetch(sem, num, session))
#             tasks.append(task)
#         await asyncio.gather(*tasks)
#
#
#
#
# loop = asyncio.get_event_loop()
# page = list(range(5201856, 5201857))
# loop.run_until_complete(downloader(page))
# loop.close()


import asyncio
import aioredis

loop = asyncio.get_event_loop()

async def go():
    d = {'qwe': 'asd'}
    redis = await aioredis.create_redis_pool(
        'redis://localhost', minsize=5,  maxsize=100, loop=loop)
    await redis.lpush('my-key', str(d))
    redis.close()
    await redis.wait_closed()


loop.run_until_complete(go())


