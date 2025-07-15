import asyncio
import websockets
import ujson as json
import random
import logging
from typing import List, Set, Callable

# -------------------- Logger --------------------
logger = logging.getLogger("BinanceStreamer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# -------------------- Message Processor --------------------
class MessageProcessor:
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def process(self, message: str):
        try:
            data = json.loads(message)
            symbol = data["data"]["s"]
            price = float(data["data"]["p"])
            await self.queue.put((symbol, price))
        except Exception as e:
            logger.error(f"[PROCESSOR] Failed to process message: {e}")


# -------------------- WebSocket Client --------------------
import os


class BinanceWebSocketClient:
    def __init__(self, on_message: Callable[[str], asyncio.Task],
                 base_url: str = os.getenv("BINANCE_WS_URL", "wss://stream.binance.com:9443")):
        self.on_message = on_message
        self.base_url = base_url.rstrip("/")

    def generate_url(self, pairs: List[str]) -> str:
        stream_path = "/".join(f"{pair.lower()}@trade" for pair in pairs)
        return f"{self.base_url}/stream?streams={stream_path}"

    async def connect(self, url: str):
        backoff = 1
        max_backoff = 60

        while True:
            try:
                logger.info(f"[WS CLIENT] Connecting to: {url}")
                async with websockets.connect(url) as ws:
                    logger.info("[WS CLIENT] Connected.")
                    backoff = 1
                    while True:
                        msg = await ws.recv()
                        await self.on_message(msg)
            except asyncio.CancelledError:
                logger.warning("[WS CLIENT] Cancelled by user.")
                break
            except Exception as e:
                logger.error(f"[WS CLIENT] Error: {e}. Reconnecting in {backoff}s...")
                await asyncio.sleep(backoff + random.uniform(0, 1))
                backoff = min(backoff * 2, max_backoff)


# -------------------- Stream Manager --------------------
class StreamManager:
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.current_pairs: Set[str] = set()
        self.task: asyncio.Task = None
        self.processor = MessageProcessor(self.queue)
        self.client = BinanceWebSocketClient(self.processor.process)

    def _generate_url(self, pairs: List[str]) -> str:
        stream_path = "/".join(f"{pair.lower()}@trade" for pair in pairs)
        return f"wss://stream.binance.com:9443/stream?streams={stream_path}"

    async def start_stream(self, pairs: List[str]):
        new_pairs = set(pairs)
        merged_pairs = self.current_pairs.union(new_pairs)

        if self.current_pairs == merged_pairs:
            logger.info(f"[MANAGER] Already streaming: {self.current_pairs}")
            return

        await self._restart_stream(list(merged_pairs))

    async def stop_stream(self, pairs_to_stop: List[str]):
        remove_set = set(pairs_to_stop)
        updated_pairs = self.current_pairs - remove_set
        removed_pairs = self.current_pairs & remove_set

        if self.current_pairs == updated_pairs:
            logger.info(f"[MANAGER] No matching pairs to stop: {pairs_to_stop}")
            return

        if not updated_pairs:
            await self._stop_all_streams()
            logger.info(f"[MANAGER] All pairs stopped: {removed_pairs}")
            return

        logger.info(f"[MANAGER] Stopping stream for: {removed_pairs}, continuing for: {updated_pairs}")
        await self._restart_stream(list(updated_pairs))

    def get_current_pairs(self) -> List[str]:
        return list(self.current_pairs)

    async def _stop_all_streams(self):
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                logger.info("[MANAGER] Stream task cancelled successfully.")
        else:
            logger.info("[MANAGER] No active stream to stop.")
        self.current_pairs.clear()
        self.task = None

    async def _restart_stream(self, pairs: List[str]):
        logger.info(f"[MANAGER] Restarting stream with pairs: {pairs}")
        await self._stop_all_streams()
        self.current_pairs = set(pairs)
        await save_current_pairs(self.current_pairs, self.persistence_file)
        url = self.client.generate_url(pairs)
        self.task = asyncio.create_task(self.client.connect(url))
