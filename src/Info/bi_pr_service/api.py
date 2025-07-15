from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.streamer import BinanceStreamer

router = APIRouter()
streamer: BinanceStreamer = None  # Will be initialized in main


class PairList(BaseModel):
    pairs: list[str]


@router.post("/start")
async def start_stream(request: Request, pair_list: PairList):
    await streamer.start_stream(pair_list.pairs)
    return {"status": "started", "streaming": list(streamer.current_pairs)}


@router.post("/remove")
async def remove_stream(request: Request, pair_list: PairList):
    await streamer.remove_pairs(pair_list.pairs)
    return {"status": "updated", "streaming": list(streamer.current_pairs)}


@router.post("/stop")
async def stop_stream():
    await streamer.stop_stream()
    return {"status": "stopped"}


@router.get("/status")
async def get_status():
    return {"currently_streaming": list(streamer.current_pairs)}


===============================================


from fastapi import FastAPI, Header, HTTPException
from app.stream_manager import StreamManager
from app.subscription_manager import SubscriptionManager
import asyncio

app = FastAPI()
queue = asyncio.Queue()
stream_manager = StreamManager(queue)
subscription_manager = SubscriptionManager(stream_manager)


@app.post("/subscribe")
async def subscribe(pair: str, x_client_id: str = Header(...)):
    await subscription_manager.subscribe(pair, x_client_id)
    return {"status": "subscribed", "pair": pair}


@app.post("/unsubscribe")
async def unsubscribe(pair: str, x_client_id: str = Header(...)):
    await subscription_manager.unsubscribe(pair, x_client_id)
    return {"status": "unsubscribed", "pair": pair}


@app.get("/status")
async def status():
    return {"subscriptions": subscription_manager.get_status()}
