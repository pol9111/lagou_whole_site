from fake_useragent import UserAgent
import redis
import motor.motor_asyncio

PROXY_URL = 'http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey='
START_PAGE = 4000000
PER_LOOP = 500

HEADERS = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
'Cache-Control': 'no-cache',
'Connection': 'keep-alive',
'Host': 'www.lagou.com',
'Pragma': 'no-cache',
'Upgrade-Insecure-Requests': '1',
'User-Agent': UserAgent().random,
}

REDIS_POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True, password='qwe123')
REDIS_CONN = redis.StrictRedis(connection_pool=REDIS_POOL)
LAGOU_COOKIES = 'lagou:cookies'
LAGOU_DONE = 'lagou:done'
LAGOU_RETRY = 'lagou:retry'
LAGOU_BLANK = 'lagou:blank'
LAGOU_ITEMS = 'lagou:items'
PROIES = 'proxies'

CLIENT = motor.motor_asyncio.AsyncIOMotorClient('mongodb://Bridi:anNBU7MD@localhost:27017')
DB = CLIENT['lagou']
TABLE = DB['job']