import asyncio
from app.streamer import binance_price_stream
from app.publisher import DebouncedPublisher

async def main():
    queue = asyncio.Queue()
    publisher = DebouncedPublisher(queue)

    await asyncio.gather(
        binance_price_stream(queue),
        publisher.start()
    )

if __name__ == "__main__":
    asyncio.run(main())
