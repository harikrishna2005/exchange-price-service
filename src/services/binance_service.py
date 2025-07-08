import httpx


class BinanceService:
    async def get_price(self, symbol: str) -> dict:
        async with httpx.AsyncClient() as client:
            url = "https://api.binance.com/api/v3/ticker/price"
            resp = await client.get(url, params={"symbol": symbol})
            resp.raise_for_status()
            data = resp.json()
            return {"symbol": symbol, "price": float(data["price"])}
