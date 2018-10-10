import redis
from fake_useragent import UserAgent

HEADERS = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
'Cache-Control': 'no-cache',
'Connection': 'keep-alive',
'Host': 'www.lagou.com',
'Pragma': 'no-cache',
# 'Referer': url,
'Upgrade-Insecure-Requests': '1',
'User-Agent': UserAgent().random,
}


REDIS_POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
REDIS_CONN = redis.StrictRedis(connection_pool=REDIS_POOL)
LAGOU_COOKIES = 'lagou:cookies'
LAGOU_DONE = 'lagou:done'
LAGOU_RETRY = 'lagou:retry'
LAGOU_BLANK = 'lagou:blank'
LAGOU_ITEMS = 'lagou:items'





