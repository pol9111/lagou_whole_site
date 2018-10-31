import aioredis
from config import LAGOU_ITEMS, TABLE


class SaveHandler(object):
    def __init__(self):
        self.lagou_items = LAGOU_ITEMS
        self.table = TABLE

    async def get_data(self, loop):
        print('开始存入mongo..')
        redis = await aioredis.create_redis_pool(
            'redis://localhost', loop=loop, password='qwe123')
        length = await redis.llen(self.lagou_items)
        items = []
        for i in range(length):
            item = await redis.rpop(self.lagou_items)
            items.append(eval(item.decode()))
        redis.close()
        await redis.wait_closed()
        await self.save_to_mongo(items)

    async def save_to_mongo(self, data):
        if data:
            await self.table.insert_many(data)

    def start_saver(self, loop):
        loop.run_until_complete(self.get_data(loop))
        print('已存入mongo..')