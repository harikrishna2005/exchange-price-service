symbols = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT",
    # Add up to 50 pairs here
]

BINANCE_WS_URL = "wss://stream.binance.com:9443/stream?streams="
REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_CHANNEL = "price_updates"
DEBOUNCE_SECONDS = 1.0
