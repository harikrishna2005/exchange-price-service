from collections import defaultdict
from typing import Set
import logging
from app.stream_manager import StreamManager  # your existing StreamManager

logger = logging.getLogger("SubscriptionManager")


class SubscriptionManager:
    def __init__(self, stream_manager: StreamManager):
        self.pair_subscriptions: dict[str, Set[str]] = defaultdict(set)
        self.stream_manager = stream_manager

    async def subscribe(self, pair: str, client_id: str):
        already_subscribed = bool(self.pair_subscriptions[pair])
        self.pair_subscriptions[pair].add(client_id)

        if not already_subscribed:
            logger.info(f"[SUBSCRIPTION] First client subscribed to {pair}, starting stream.")
            await self.stream_manager.start_stream([pair])
        else:
            logger.info(f"[SUBSCRIPTION] Added {client_id} to {pair}. Total: {len(self.pair_subscriptions[pair])}")

    async def unsubscribe(self, pair: str, client_id: str):
        self.pair_subscriptions[pair].discard(client_id)

        if not self.pair_subscriptions[pair]:
            logger.info(f"[SUBSCRIPTION] No clients left for {pair}, stopping stream.")
            await self.stream_manager.stop_stream([pair])
            del self.pair_subscriptions[pair]
        else:
            logger.info(
                f"[SUBSCRIPTION] Removed {client_id} from {pair}. Remaining: {len(self.pair_subscriptions[pair])}")

    def get_status(self):
        return {pair: list(clients) for pair, clients in self.pair_subscriptions.items()}
