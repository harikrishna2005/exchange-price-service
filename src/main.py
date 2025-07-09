from fastapi import FastAPI
from src.routers.price_router import router as price_router

from contextlib import asynccontextmanager


async def lifespan(myapp: FastAPI):
    # This is where you can initialize resources or connections
    print("Starting Exchange Price Service...")
    yield  # This is where the app runs
    # Cleanup code can go here if needed
    print("Stopping Exchange Price Service...")


app = FastAPI(title="Exchange Price Service")

app.include_router(price_router, prefix="/price", tags=["Price"])


# app.add_event_handler("startup", lambda: print("Starting Exchange Price Service..."))
@app.get("/")
async def root():
    return {"message": "Welcome to the Exchange Price Service!"}
