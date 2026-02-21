from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("opencore.api")

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
    logger.error(f"Unhandled exception processing request {request.method} {request.url.path}: {exc}")
    traceback.print_exc()

    # Return generic 500 error for unexpected exceptions
    # In production, we hide details to prevent information leakage
    details = None
    if os.getenv("APP_ENV", "production") == "development":
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
