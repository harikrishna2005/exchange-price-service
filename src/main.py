from fastapi import FastAPI, Request
from src.routers.price_router import router as price_router
from src.common_lib.logging import configure_logging, LogLevel
import logging
from contextlib import asynccontextmanager

from src.utilities.middleware import ResponseWrapperMiddleware

from src.utilities.utils import success_response, error_response, APIResponse

configure_logging(LogLevel.DEBUG)


async def lifespan(myapp: FastAPI):
    # This is where you can initialize resources or connections
    print("Starting Exchange Price Service...")
    yield  # This is where the app runs
    # Cleanup code can go here if needed
    print("Stopping Exchange Price Service...")


app = FastAPI(title="Exchange Price Service")

app.include_router(price_router, prefix="/price", tags=["Price"])
app.add_middleware(ResponseWrapperMiddleware)


# *************  Logging Request and Response Middleware *************
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     logging.info(f"Request: {request.method} {request.url}")
#     response = await call_next(request)
#     logging.info(f"Response status: {response.status_code}")
#     return response

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     request_body = await request.body()
#     logging.info(f"Request: {request.method} {request.url} | Body: {request_body.decode('utf-8', errors='ignore')}")
#
#     response = await call_next(request)
#     response_body = b""
#     async for chunk in response.body_iterator:
#         response_body += chunk
#     logging.info(f"Response status: {response.status_code} | Body: {response_body.decode('utf-8', errors='ignore')}")
#
#     # Recreate the response with the original body
#     from starlette.responses import Response
#     return Response(content=response_body, status_code=response.status_code, headers=dict(response.headers),
#                     media_type=response.media_type)
#

# ******************************************************

# app.add_event_handler("startup", lambda: print("Starting Exchange Price Service..."))
@app.get("/", response_model=APIResponse)
async def root():
    logging.info(f"This is super logging")
    logging.debug(f"This is DEBUG logging")
    logging.warning(f"This is DEBUG logging")
    logging.error(f"This is DEBUG logging")
    logging.critical(f"This is DEBUG logging")
    # 1 / 0

    # try:
    #     1 / 0
    # except Exception:
    #     logging.exception(f"This is exception  logging")
    #     raise ValueError("I for zero division exception")
    myresponse = success_response(
        message="Welcome to the Exchange Price Service!",
        data={"status": "Service is running"}
    )
    return myresponse
    # return {"message": "Welcome to the Exchange udpated Price Service!"}
