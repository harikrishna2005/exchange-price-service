import asyncio
import logging
from app.streamer import StreamManager

logger = logging.getLogger("BinanceStreamer")


async def health_check(manager: StreamManager):
    while True:
        if manager.task and manager.task.done():
            logger.error("[WATCHDOG] Stream task died. Restarting...")
            await manager._restart_stream(list(manager.current_pairs))
        await asyncio.sleep(10)  # check every 10 seconds
