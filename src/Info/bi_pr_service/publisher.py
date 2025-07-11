import asyncio
import time
import redis.asyncio as aioredis
from app.config import REDIS_HOST, REDIS_PORT, REDIS_CHANNEL, DEBOUNCE_SECONDS
import ujson as json

class DebouncedPublisher:
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.redis = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        self.latest_price_map = {}  # {symbol: price}

    async def consume_queue(self):
        """ Continuously consume from queue and update latest prices. """
        while True:
            symbol, price = await self.queue.get()
            self.latest_price_map[symbol] = price

    async def publish_loop(self):
        """ Periodically publish latest prices per symbol. """
        while True:
            await asyncio.sleep(DEBOUNCE_SECONDS)
            for symbol, price in self.latest_price_map.items():
                await self.redis.publish(REDIS_CHANNEL, json.dumps({
                    "symbol": symbol,
                    "price": price
                }))
                print(f"[PUBLISHED] {symbol}: {price}")

    async def start(self):
        await asyncio.gather(
            self.consume_queue(),
            self.publish_loop()
        )
