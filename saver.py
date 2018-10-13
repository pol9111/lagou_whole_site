import aioredis
from config import LAGOU_ITEMS, TABLE


async def get_data(loop):
    print('开始存入mongo..')
    redis = await aioredis.create_redis_pool(
        'redis://localhost', loop=loop)
    length = await redis.llen(LAGOU_ITEMS)
    items = []
    for i in range(length):
        item = await redis.rpop(LAGOU_ITEMS)
        items.append(eval(item.decode()))
    redis.close()
    await redis.wait_closed()
    await save_to_mongo(items)


async def save_to_mongo(data):
    if data:
        await TABLE.insert_many(data)


def start_saver(loop):
    loop.run_until_complete(get_data(loop))
    print('已存入mongo..')