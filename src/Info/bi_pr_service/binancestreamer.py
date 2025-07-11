import asyncio
import ujson as json
import websockets
from app.config import symbols, BINANCE_WS_URL

async def binance_price_stream(queue: asyncio.Queue):
    stream_names = "/".join([f"{s.lower()}@trade" for s in symbols])
    url = BINANCE_WS_URL + stream_names

    async with websockets.connect(url) as ws:
        print(f"[STREAM] Connected to Binance: {url}")

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)

                symbol = data["data"]["s"]
                price = float(data["data"]["p"])

                await queue.put((symbol, price))
            except Exception as e:
                print("[ERROR] WebSocket:", e)
                await asyncio.sleep(5)
