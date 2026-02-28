from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from opencore.config import settings
from opencore.core.context import request_id_ctx
import logging
import uuid

# Configure logging
logger = logging.getLogger("opencore.api")


async def request_id_middleware(request: Request, call_next):
    """
    Middleware to generate a unique request ID for every request,
    store it in a context variable for logging, and return it in headers.
    """
    request_id = str(uuid.uuid4())
    token = request_id_ctx.set(request_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        request_id_ctx.reset(token)


class ErrorDetails(BaseModel):
    code: str
    message: str
    details: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetails


async def global_exception_handler(request: Request, exc: Exception):
    """
    Centralized exception handler for the API.
    Catches all exceptions and returns a consistent JSON error response.
    """

    # Handle Request Validation Errors
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error=ErrorDetails(
                    code="UNPROCESSABLE_ENTITY",
                    message="Request validation failed.",
                    details=str(exc.errors())
                )
            ).model_dump()
        )

    # Handle specific HTTPExceptions
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetails(
                    code=f"HTTP_{exc.status_code}",
                    message=exc.detail,
                )
            ).model_dump()
        )

    # Log unexpected errors with full traceback
    logger.exception(
        f"Unhandled exception processing request "
        f"{request.method} {request.url.path}: {exc}"
    )

    # Return generic 500 error for unexpected exceptions
    # In production, we hide details to prevent information leakage
    details = None
    if settings.is_dev:
        details = str(exc)

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorDetails(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred.",
                details=details
            )
        ).model_dump()
    )
