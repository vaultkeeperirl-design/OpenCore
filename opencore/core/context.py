from contextvars import ContextVar
from typing import Optional

# Context variable to store the request ID for the current execution context.
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
