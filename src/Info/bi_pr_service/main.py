import asyncio
from app.streamer import BinanceStreamer
from app.publisher import DebouncedPublisher
from app.config import symbols


async def main():
    queue = asyncio.Queue()
    publisher = DebouncedPublisher(queue)
    streamer = BinanceStreamer(queue)

    await asyncio.gather(
        streamer.start_stream(symbols),
        publisher.start()
    )


if __name__ == "__main__":
    asyncio.run(main())

=================================================




import asyncio
from fastapi import FastAPI
from app.api import router, streamer
from app.streamer import BinanceStreamer
from app.publisher import DebouncedPublisher

from app.config import symbols

app = FastAPI(title="Binance Streamer API")
app.include_router(router)

@app.on_event("startup")
async def startup():
    queue = asyncio.Queue()
    streamer_instance = BinanceStreamer(queue)
    publisher = DebouncedPublisher(queue)

    # Register globally in api.py
    from app import api
    api.streamer = streamer_instance

    asyncio.create_task(publisher.start())

=================================================



from your_module.persistence import load_last_pairs

@app.on_event("startup")
async def startup():
    queue = asyncio.Queue()
    manager = StreamManager(queue)
    last_pairs = await load_last_pairs()
    if last_pairs:
        await manager.start_stream(list(last_pairs))


============
how to launch
BINANCE_WS_URL="wss://testnet.binance.vision" uvicorn main:app


=============================

#  with HEALTH CHECK

import asyncio
from fastapi import FastAPI
from app.streamer import StreamManager
from app.health import health_check  # we'll write this
import logging

logger = logging.getLogger("BinanceStreamer")
app = FastAPI()

@app.on_event("startup")
async def startup():
    queue = asyncio.Queue()
    app.state.manager = StreamManager(queue)

    # Optional: load last pairs if using persistence
    # last_pairs = await load_last_pairs()
    # await app.state.manager.start_stream(list(last_pairs))

    # 🔁 Start the watchdog in background
    asyncio.create_task(health_check(app.state.manager))
====================
# Build and run command
# Build Docker image:
docker build -t binance-streamer .   (build docker image)

# Run with docker
docker run -d -p 8000:8000 --name streamer binance-streamer


# Or use docker-compose:
docker-compose up --build
======================================


from fastapi import FastAPI, Header, HTTPException
from app.stream_manager import StreamManager
from app.subscription_manager import SubscriptionManager
import asyncio

app = FastAPI()
queue = asyncio.Queue()
stream_manager = StreamManager(queue)
subscription_manager = SubscriptionManager(stream_manager)


@app.post("/subscribe")
async def subscribe(pair: str, x_client_id: str = Header(...)):
    if x_client_id in subscription_manager.pair_subscriptions[pair]:
        return api_response(
            status="ok",
            message=f"Already subscribed: {pair} by client {x_client_id}",
            data={"pair": pair}
        )
    await subscription_manager.subscribe(pair, x_client_id)
    return api_response(
        status="ok",
        message=f"Subscribed to {pair}",
        data={"pair": pair}
    )


@app.post("/unsubscribe")
async def unsubscribe(pair: str, x_client_id: str = Header(...)):
    if pair not in subscription_manager.pair_subscriptions:
        return api_response(
            status="ok",
            message=f"No active subscription for {pair}",
            data={"pair": pair}
        )
    await subscription_manager.unsubscribe(pair, x_client_id)
    return api_response(
        status="ok",
        message=f"Unsubscribed from {pair}",
        data={"pair": pair}
    )


@app.get("/status")
async def status():
    return {"subscriptions": subscription_manager.get_status()}
