import asyncio
import websockets
import ujson as json
import random


class BinanceStreamer:
    def __init__(self, queue: asyncio.Queue):
        self.task = None
        self.queue = queue
        self.current_pairs = set()  # Set only inside stream()

    async def stream(self, pairs):
        self.current_pairs = set(pairs)
        stream_path = "/".join(f"{pair.lower()}@trade" for pair in pairs)
        url = f"wss://stream.binance.com:9443/stream?streams={stream_path}"

        backoff = 1  # Initial backoff in seconds
        max_backoff = 60  # Max backoff limit

        while True:
            try:
                print(f"[STREAM] Connecting to: {url}")
                async with websockets.connect(url) as ws:
                    print(f"[CONNECTED] Streaming: {pairs}")
                    backoff = 1  # Reset backoff after successful connection
                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        symbol = data["data"]["s"]
                        price = float(data["data"]["p"])
                        await self.queue.put((symbol, price))
            except asyncio.CancelledError:
                print("[STREAM] Cancelled by user")
                break
            except Exception as e:
                print(f"[ERROR] WebSocket error: {e}. Retrying in {backoff} seconds...")
                await asyncio.sleep(backoff + random.uniform(0, 1))  # jitter
                backoff = min(backoff * 2, max_backoff)

    async def start_stream(self, pairs):
        new_pairs = set(pairs)
        merged_pairs = self.current_pairs.union(new_pairs)

        if self.current_pairs == merged_pairs:
            print(f"[STREAM] Already streaming: {self.current_pairs}")
            return

        if self.task and not self.task.done():
            await self.stop_stream()

        self.task = asyncio.create_task(self.stream(list(merged_pairs)))

    async def remove_pairs(self, pairs_to_remove):
        remove_set = set(pairs_to_remove)
        updated_pairs = self.current_pairs - remove_set

        if updated_pairs == self.current_pairs:
            print(f"[STREAM] No matching pairs to remove: {pairs_to_remove}")
            return

        if self.task and not self.task.done():
            await self.stop_stream()

        if updated_pairs:
            self.task = asyncio.create_task(self.stream(list(updated_pairs)))
        else:
            print("[STREAM] All pairs removed. No stream started.")

    async def stop_stream(self):
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                print("[STREAM] Cancelled successfully.")
            self.current_pairs.clear()
        else:
            print("[STREAM] No active stream to stop.")
