import asyncio
import redis.asyncio as aioredis
import ujson as json
from app.config import REDIS_HOST, REDIS_PORT, REDIS_CHANNEL, DEBOUNCE_SECONDS


class DebouncedPublisher:
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.redis = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        self.latest_price_map = {}  # Holds only the most recent price per symbol

    async def consume_queue(self):
        while True:
            symbol, price = await self.queue.get()
            self.latest_price_map[symbol] = price

    async def publish_loop(self):
        while True:
            await asyncio.sleep(DEBOUNCE_SECONDS)
            for symbol, price in self.latest_price_map.items():
                payload = json.dumps({"symbol": symbol, "price": price})
                await self.redis.publish(REDIS_CHANNEL, payload)
                print(f"[PUBLISHED] {symbol}: {price}")

    async def start(self):
        await asyncio.gather(
            self.consume_queue(),
            self.publish_loop()
        )
