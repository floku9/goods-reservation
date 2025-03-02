from typing import Callable

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from app.routes import reservation_router
from app.utils.exceptions import ReservationException
from app.utils.logging import logger
from settings import backend_settings

app = FastAPI(
    title="Goods Reservation API",
    version="0.1.0",
    docs_url="/docs",
)
app.include_router(reservation_router)


@app.exception_handler(ReservationException)
async def reservation_exception_handler(request, exc: ReservationException):
    logger.error(
        f"Reservation Exception: {exc.__class__.__name__} - "
        f"Status Code: {exc.status_code} - "
        f"Message: {exc.response.message} - "
        f"Reservation ID: {exc.response.reservation_id}"
    )
    return JSONResponse(status_code=exc.status_code, content=exc.response.model_dump())


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    logger.error(
        f"HTTP Exception: Status {exc.status_code} - "
        f"Detail: {exc.detail} - "
        f"URL: {request.method} {request.url}"
    )
    return JSONResponse(
        status_code=exc.status_code, content={"status": "error", "message": exc.detail}
    )


@app.middleware("http")
async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Logs the incoming request and outgoing response for the current HTTP request.

    This middleware function is responsible for logging the details of the incoming HTTP request
    and the outgoing HTTP response. It logs the request method, URL,
    and the client's IP address and port. After the request is processed, it also logs the
    response status code, request method, and URL.

    """
    log_message = (
        f" - Request: {request.method} {request.url} - "
        f"Client: {request.client.host}:{request.client.port}"  # type: ignore
    )

    # Additional logging for POST and PUT requests (not sure if it's right, because of sensitive data)
    if request.method in ["POST", "PUT"]:
        body = await request.body()
        if body:
            log_message += f" - Body: {body.decode('utf-8')}"

    logger.info(log_message)
    response = await call_next(request)

    logger.info(
        f"Response: Status {response.status_code} - Method: {request.method} - URL: {request.url}"
    )

    return response


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=backend_settings.BACKEND_HOST,
        port=backend_settings.BACKEND_PORT,
        reload=True,
    )
