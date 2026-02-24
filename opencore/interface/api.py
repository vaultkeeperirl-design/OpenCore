from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager
from opencore.core.swarm import Swarm
from opencore.interface.middleware import global_exception_handler, request_id_middleware
from opencore.core.scheduler import AsyncScheduler
from opencore.interface.heartbeat import heartbeat_manager
from opencore.config import settings, ALLOWED_CONFIG_KEYS
import logging
import os
import tempfile
from starlette.concurrency import run_in_threadpool
from opencore.auth import get_auth_status
from opencore.interface.auth_routes import auth_router
from opencore.audio.transcriber import transcribe_audio

# Initialize Scheduler
scheduler = AsyncScheduler()

# Initialize Swarm
swarm = Swarm()

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
        # Run blocking swarm.chat in a threadpool to avoid blocking the event loop
        response = await run_in_threadpool(
            swarm.chat,
            "SYSTEM HEARTBEAT: Current time check. Review recent user requests and status. "
            "If there are pending tasks or if you can proactively assist with the user's goals based on previous context, "
            "please execute them or suggest the next step. If everything is idle, just acknowledge."
        )
        logger.info(f"Heartbeat Response: {response}")
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

# Register centralized error handler
app.add_exception_handler(Exception, global_exception_handler)

# Register request ID middleware
app.middleware("http")(request_id_middleware)

# Include Auth Router
app.include_router(auth_router)

class ChatRequest(BaseModel):
    message: str
    attachments: Optional[List[Dict[str, str]]] = None

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

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # In a real streaming scenario, we would use Server-Sent Events (SSE) or WebSockets.
    # For this MVP, we block and return the final response, but the frontend shows a loading state.

    # We could potentially capture logs here by inspecting the agent's recent messages
    # but the current `think` method returns just the string.

    response = swarm.chat(request.message, attachments=request.attachments)

    return ChatResponse(
        response=response,
        agents=list(swarm.agents.keys()),
        graph=swarm.get_graph_data(),
        activity_log=swarm.current_turn_activity
    )

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Accepts an audio file upload and returns the transcription.
    """
    try:
        # Create a temporary file to save the upload
        suffix = os.path.splitext(file.filename)[1] if file.filename else ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Run transcription in a threadpool to avoid blocking event loop
        # This will lazy-load the model on first request
        text = await run_in_threadpool(transcribe_audio, tmp_path)

        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        return {"text": text}
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        # Clean up if needed
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        # Return empty text so frontend knows it failed but doesn't crash
        # Alternatively return 500, but keeping it simple
        return {"error": str(e), "text": ""}

@app.get("/agents")
async def get_agents():
    return {
        "agents": list(swarm.agents.keys()),
        "graph": swarm.get_graph_data()
    }

@app.delete("/agents/{name}")
async def delete_agent(name: str):
    result = swarm.remove_agent(name)
    if "Error" in result:
        return {"status": "error", "message": result}
    return {"status": "success", "message": result, "graph": swarm.get_graph_data()}

@app.post("/agents/{name}/toggle")
async def toggle_agent(name: str):
    result = swarm.toggle_agent(name)
    if "Error" in result:
        return {"status": "error", "message": result}
    return {"status": "success", "message": result, "graph": swarm.get_graph_data()}

@app.get("/heartbeat")
async def get_heartbeat():
    return heartbeat_manager.get_status()

@app.get("/auth/status")
async def get_authentication_status():
    """Returns the status of OAuth providers."""
    return get_auth_status()

@app.get("/config")
async def get_config():
    """Returns the current configuration (masked)."""
    # Force reload to ensure we have the latest environment state
    settings.reload()
    return {
        "LLM_MODEL": settings.llm_model or "gpt-4o",
        "HEARTBEAT_INTERVAL": str(settings.heartbeat_interval),
        "VERTEX_PROJECT": settings.vertex_project,
        "VERTEX_LOCATION": settings.vertex_location,
        "OLLAMA_API_BASE": settings.ollama_api_base,
        # Boolean flags for sensitive keys
        "HAS_OPENAI_KEY": settings.has_openai_key,
        "HAS_ANTHROPIC_KEY": settings.has_anthropic_key,
        "HAS_MISTRAL_KEY": settings.has_mistral_key,
        "HAS_XAI_KEY": settings.has_xai_key,
        "HAS_DASHSCOPE_KEY": settings.has_dashscope_key,
        "HAS_GEMINI_KEY": settings.has_gemini_key,
        "HAS_GROQ_KEY": settings.has_groq_key,
    }

@app.post("/config")
async def update_config(config: Dict[str, Any]):
    """Updates the .env file and reloads configuration."""
    try:
        # Filter out keys not in the allowed list (e.g., read-only flags like HAS_OPENAI_KEY)
        valid_config = {k: v for k, v in config.items() if k in ALLOWED_CONFIG_KEYS}

        settings.update_env(valid_config)
        swarm.update_settings()
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "success", "message": "Configuration updated."}

# Mount static files
app.mount("/", StaticFiles(directory="opencore/interface/static", html=True), name="static")
