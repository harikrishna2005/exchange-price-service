from fastapi import APIRouter, HTTPException
from src.models.price_request import PriceRequest
from src.services.price_service import PriceService

router = APIRouter()
price_service = PriceService()

@router.post("/")
async def get_price(request: PriceRequest):
    try:
        return await price_service.get_price(request.exchange, request.symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
