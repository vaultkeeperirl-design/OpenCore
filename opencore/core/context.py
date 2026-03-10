from contextvars import ContextVar
from typing import Optional, List, Dict, Any

# Context variable to store the request ID for the current execution context.
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

# Context variable to store the activity log for the current turn/request execution context.
activity_log_ctx: ContextVar[Optional[List[Dict[str, Any]]]] = ContextVar("activity_log", default=None)
