import redis.asyncio as aioredis

async def listen():
    redis = aioredis.Redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe("price_updates")

    async for message in pubsub.listen():
        if message["type"] == "message":
            print("New Price:", message["data"])

asyncio.run(listen())
