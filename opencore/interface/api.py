from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from typing import Dict, Any, List, Optional
from pathlib import Path
from contextlib import asynccontextmanager
from opencore.core.swarm import Swarm
from opencore.core.context import activity_log_ctx
from opencore.interface.middleware import global_exception_handler, request_id_middleware
from opencore.interface.rate_limit import RateLimitMiddleware
from opencore.core.scheduler import AsyncScheduler
from opencore.interface.heartbeat import heartbeat_manager
from opencore.config import settings, ALLOWED_CONFIG_KEYS

import logging

from starlette.concurrency import run_in_threadpool
from opencore.auth import get_auth_status
from opencore.interface.auth_routes import auth_router
from opencore.audio.service import AudioService, AudioValidationError, AudioSizeError

# Initialize Scheduler
scheduler = AsyncScheduler()

# Initialize Swarm
swarm = Swarm()

# Initialize AudioService
audio_service = AudioService()

logger = logging.getLogger("opencore.api")

async def run_proactive_heartbeat():
    """
    Periodic task to check system health and trigger proactive agent behavior.
    """
    # Log heartbeat
    await heartbeat_manager.log_heartbeat()

    # Trigger proactive agent logic
    try:
        logger.info("Executing proactive heartbeat task...")
        # Isolate request-scoped activity context for proactive heartbeat thread
        token = activity_log_ctx.set([])
        try:
            # Run blocking swarm.chat in a threadpool to avoid blocking the event loop
            response = await run_in_threadpool(
                swarm.chat,
                "SYSTEM HEARTBEAT: Current time check. Review recent user requests and status. "
                "If there are pending tasks or if you can proactively assist with the user's goals based on previous context, "
                "please execute them or suggest the next step. If everything is idle, just acknowledge."
            )
            logger.info(f"Heartbeat Response: {response}")
        finally:
            activity_log_ctx.reset(token)
    except Exception as e:
        logger.error(f"Error during proactive heartbeat: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register heartbeat job
    scheduler.add_job(
        run_proactive_heartbeat,
        settings.heartbeat_interval,
        "system_heartbeat"
    )

    # Start scheduler
    scheduler.start()

    yield

    # Stop scheduler
    scheduler.stop()

app = FastAPI(lifespan=lifespan)

# Register CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],  # Allow specific origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Register centralized error handler
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, global_exception_handler)
app.add_exception_handler(RequestValidationError, global_exception_handler)

# Register request ID middleware
app.middleware("http")(request_id_middleware)

# Register rate limit middleware (max 600 requests per minute to accommodate tests and normal usage)
app.add_middleware(RateLimitMiddleware, max_requests=600, window_seconds=60)

# Include Auth Router
app.include_router(auth_router)

class Attachment(BaseModel):
    name: str
    type: str
    content: str

    @field_validator('content')
    @classmethod
    def validate_content_size(cls, v: str) -> str:
        # 15MB limit for Base64 (approx 11MB file size)
        if len(v) > 15 * 1024 * 1024:
            raise ValueError("File too large")
        return v

class ChatRequest(BaseModel):
    message: str
    attachments: Optional[List[Attachment]] = None

class ActivityItem(BaseModel):
    type: str  # interaction, lifecycle
    subtype: Optional[str] = None # create, remove
    source: Optional[str] = None
    target: Optional[str] = None
    summary: Optional[str] = None
    agent: Optional[str] = None
    timestamp: str

class ChatResponse(BaseModel):
    response: str
    agents: list
    tool_logs: list = [] # Future: detailed logs
    graph: Optional[Dict[str, Any]] = None
    activity_log: List[ActivityItem] = []

class ConfigRequest(BaseModel):
    LLM_MODEL: Optional[str] = None
    HEARTBEAT_INTERVAL: Optional[int] = None
    VERTEX_PROJECT: Optional[str] = None
    VERTEX_LOCATION: Optional[str] = None
    OLLAMA_API_BASE: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    MISTRAL_API_KEY: Optional[str] = None
    XAI_API_KEY: Optional[str] = None
    DASHSCOPE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    LOG_LEVEL: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REFRESH_TOKEN: Optional[str] = None
    ALLOW_UNSAFE_SYSTEM_ACCESS: Optional[str] = None
    MAX_TURNS: Optional[int] = None
    MAX_HISTORY: Optional[int] = None

class TranscribeResponse(BaseModel):
    text: str
    error: Optional[str] = None

class AgentListResponse(BaseModel):
    agents: List[str]
    graph: Dict[str, Any]

class AgentActionResponse(BaseModel):
    status: str
    message: str
    graph: Optional[Dict[str, Any]] = None

class HeartbeatResponse(BaseModel):
    status: str
    last_heartbeat: Optional[str] = None
    uptime: str
    version: str
    start_time: str

class AuthStatusResponse(BaseModel):
    google: bool
    qwen: bool

class ConfigResponse(BaseModel):
    LLM_MODEL: str
    HEARTBEAT_INTERVAL: str
    VERTEX_PROJECT: Optional[str] = None
    VERTEX_LOCATION: Optional[str] = None
    OLLAMA_API_BASE: Optional[str] = None
    HAS_OPENAI_KEY: bool
    HAS_ANTHROPIC_KEY: bool
    HAS_MISTRAL_KEY: bool
    HAS_XAI_KEY: bool
    HAS_DASHSCOPE_KEY: bool
    HAS_GEMINI_KEY: bool
    HAS_GROQ_KEY: bool

class ConfigUpdateResponse(BaseModel):
    status: str
    message: str

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # In a real streaming scenario, we would use Server-Sent Events (SSE) or WebSockets.
    # For this MVP, we block and return the final response, but the frontend shows a loading state.

    # Convert Pydantic models to dicts for internal processing
    attachments_dict = [a.model_dump() for a in request.attachments] if request.attachments else None

    # Isolate request-scoped activity log to prevent thread race conditions
    token = activity_log_ctx.set([])
    try:
        response = swarm.chat(request.message, attachments=attachments_dict)
        activity_log = activity_log_ctx.get()
    finally:
        activity_log_ctx.reset(token)

    return ChatResponse(
        response=response,
        agents=list(swarm.agents.keys()),
        graph=swarm.get_graph_data(),
        activity_log=activity_log or []
    )

@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...)):
    """
    Accepts an audio file upload and returns the transcription.
    Enforces file size limit (25MB) and extension validation.
    """
    try:
        text = await audio_service.process_upload(file)
        return TranscribeResponse(text=text)

    except (AudioValidationError, AudioSizeError) as e:
        # Return 200 with error to maintain API contract
        return TranscribeResponse(error=str(e), text="")
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        # Return a generic error message to prevent information leakage
        return TranscribeResponse(error="Transcription failed due to an internal error.", text="")

@app.get("/agents", response_model=AgentListResponse)
def get_agents():
    return AgentListResponse(
        agents=list(swarm.agents.keys()),
        graph=swarm.get_graph_data()
    )

@app.delete("/agents/{name}", response_model=AgentActionResponse)
def delete_agent(name: str):
    swarm.remove_agent(name)
    return AgentActionResponse(
        status="success",
        message=f"Agent '{name}' removed.",
        graph=swarm.get_graph_data()
    )

@app.post("/agents/{name}/toggle", response_model=AgentActionResponse)
def toggle_agent(name: str):
    result = swarm.toggle_agent(name)
    return AgentActionResponse(
        status="success",
        message=result,
        graph=swarm.get_graph_data()
    )

@app.get("/heartbeat", response_model=HeartbeatResponse)
def get_heartbeat():
    return HeartbeatResponse(**heartbeat_manager.get_status())

@app.get("/auth/status", response_model=AuthStatusResponse)
def get_authentication_status():
    """Returns the status of OAuth providers."""
    return AuthStatusResponse(**get_auth_status())

@app.get("/config", response_model=ConfigResponse)
def get_config():
    """Returns the current configuration (masked)."""
    # Force reload to ensure we have the latest environment state
    settings.reload()
    return ConfigResponse(
        LLM_MODEL=settings.llm_model or "gpt-4o",
        HEARTBEAT_INTERVAL=str(settings.heartbeat_interval),
        VERTEX_PROJECT=settings.vertex_project,
        VERTEX_LOCATION=settings.vertex_location,
        OLLAMA_API_BASE=settings.ollama_api_base,
        # Boolean flags for sensitive keys
        HAS_OPENAI_KEY=settings.has_openai_key,
        HAS_ANTHROPIC_KEY=settings.has_anthropic_key,
        HAS_MISTRAL_KEY=settings.has_mistral_key,
        HAS_XAI_KEY=settings.has_xai_key,
        HAS_DASHSCOPE_KEY=settings.has_dashscope_key,
        HAS_GEMINI_KEY=settings.has_gemini_key,
        HAS_GROQ_KEY=settings.has_groq_key,
    )

@app.post("/config", response_model=ConfigUpdateResponse)
def update_config(config: ConfigRequest):
    """Updates the .env file and reloads configuration."""
    try:
        # Filter out keys not in the allowed list (e.g., read-only flags like HAS_OPENAI_KEY)
        # Now validated by ConfigRequest Pydantic model
        config_dict = config.model_dump(exclude_unset=True)
        valid_config = {k: v for k, v in config_dict.items() if k in ALLOWED_CONFIG_KEYS}

        settings.update_env(valid_config)
        swarm.update_settings()
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        return ConfigUpdateResponse(status="error", message=str(e))

    return ConfigUpdateResponse(status="success", message="Configuration updated.")

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
