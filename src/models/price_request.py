from pydantic import BaseModel

class PriceRequest(BaseModel):
    exchange: str
    symbol: str
