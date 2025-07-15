# middlewares.py
import uuid
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi.encoders import jsonable_encoder
from src.utilities.utils import success_response, error_response

from src.common_lib.logging import configure_logging, LogLevel, _trace_local
import logging

configure_logging(LogLevel.DEBUG)


# logger = logging.getLogger("api-logger")
# logging.basicConfig(level=logging.INFO)


class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id  # Attach to request
        _trace_local.trace_id = trace_id  # <-- Setting the trace_id  and is used for each logging message
        # ******how to use the trace_id in the request context?********
        # # In your route handler or anywhere downstream
        # trace_id = getattr(request.state, "trace_id", None)
        # logging.info(f"[{trace_id}] Processing user data")
        # # ******************************************************

        try:
            # logging.debug(f"[{trace_id}] Request ID: {trace_id}")
            logging.info(f"[INCOMING REQUEST] : {request.method} {request.url}")
            response = await call_next(request)

            logging.info(f"[INCOMING RESPONSE] : Response status: {response.status_code}")
            # return JSONResponse(content=jsonable_encoder(wrapped), status_code=200)
            return response

            # if response.status_code == 200 and response.media_type == "application/json":
            #     body = await response.body()
            #     logging.info(f"[{trace_id}] Response 200 - Wrapping response")
            #     wrapped = success_response(
            #         message="Request processed successfully",
            #         data=response.media_type == "application/json" and response.body,
            #         trace_id=trace_id,
            #     )
            #     return JSONResponse(content=jsonable_encoder(wrapped))

            # return response
        except Exception as e:
            logging.exception(f"[{trace_id}] Unhandled Error: {str(e)}")
            error = error_response(f"Internal Server Error  :    {str(e)}", trace_id)
            return JSONResponse(content=jsonable_encoder(error), status_code=500)
        finally:
            logging.info(f"Request processing completed for trace_id: {trace_id}")
            _trace_local.trace_id = None  # Clean up after request
            # Optionally, you can log the trace_id at the end of the request
            # logging.info(f"[{trace_id}] Request completed")
