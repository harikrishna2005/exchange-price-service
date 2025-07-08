import httpx


async def fetch_json(url: str, params: dict = None, headers: dict = None) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
