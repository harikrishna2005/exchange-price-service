from services.binance_service import BinanceService
from services.coinbase_service import CoinbaseService  # future



class PriceService:
    def __init__(self):
        self.exchange_map = {
            "binance": BinanceService(),
            # "coinbase": CoinbaseService(),
        }

    async def get_price(self, exchange: str, symbol: str) -> dict:
        exchange = exchange.lower()
        if exchange not in self.exchange_map:
            raise ValueError(f"Exchange '{exchange}' not supported")
        return await self.exchange_map[exchange].get_price(symbol)
