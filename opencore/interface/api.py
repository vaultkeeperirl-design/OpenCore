from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any
from contextlib import asynccontextmanager
from opencore.core.swarm import Swarm
from opencore.interface.middleware import global_exception_handler
from opencore.core.scheduler import AsyncScheduler
from opencore.interface.heartbeat import heartbeat_manager
from opencore.config import settings
import logging
import os
from starlette.concurrency import run_in_threadpool
from opencore.auth import get_auth_status

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

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    agents: list
    tool_logs: list = [] # Future: detailed logs

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # In a real streaming scenario, we would use Server-Sent Events (SSE) or WebSockets.
    # For this MVP, we block and return the final response, but the frontend shows a loading state.

    # We could potentially capture logs here by inspecting the agent's recent messages
    # but the current `think` method returns just the string.

    response = swarm.chat(request.message)

    return ChatResponse(
        response=response,
        agents=list(swarm.agents.keys())
    )

@app.get("/agents")
async def get_agents():
    return {"agents": list(swarm.agents.keys())}

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
    return {
        "LLM_MODEL": os.getenv("LLM_MODEL", "gpt-4o"),
        "HEARTBEAT_INTERVAL": os.getenv("HEARTBEAT_INTERVAL", "3600"),
        "VERTEX_PROJECT": os.getenv("VERTEX_PROJECT", ""),
        "VERTEX_LOCATION": os.getenv("VERTEX_LOCATION", ""),
        "OLLAMA_API_BASE": os.getenv("OLLAMA_API_BASE", ""),
        # Boolean flags for sensitive keys
        "HAS_OPENAI_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "HAS_ANTHROPIC_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
        "HAS_MISTRAL_KEY": bool(os.getenv("MISTRAL_API_KEY")),
        "HAS_XAI_KEY": bool(os.getenv("XAI_API_KEY")), # Grok
        "HAS_DASHSCOPE_KEY": bool(os.getenv("DASHSCOPE_API_KEY")),
        "HAS_GEMINI_KEY": bool(os.getenv("GEMINI_API_KEY")),
        "HAS_GROQ_KEY": bool(os.getenv("GROQ_API_KEY")),
    }

@app.post("/config")
async def update_config(config: Dict[str, Any]):
    """Updates the .env file and reloads configuration."""
    env_path = ".env"
    existing_env = {}

    # Read existing .env if present
    if os.path.exists(env_path):
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        existing_env[key] = val
        except Exception as e:
            logger.error(f"Error reading .env: {e}")

    # Update with new values
    for k, v in config.items():
        if v is not None:
            val = str(v)
            # Auto-correct known broken model strings before saving
            if k == "LLM_MODEL":
                if val == "gemini/gemini-1.5-flash":
                    val = "gemini/gemini-1.5-flash-latest"
                elif val == "openai/grok-2-1212":
                    val = "xai/grok-2-vision-1212"

            # If value is empty string, we set it (clearing the key effectively if we write it as KEY=)
            existing_env[k] = val

    # Write back to .env
    try:
        with open(env_path, "w") as f:
            for k, v in existing_env.items():
                f.write(f"{k}={v}\n")
    except Exception as e:
        logger.error(f"Error writing .env: {e}")
        return {"status": "error", "message": str(e)}

    # Reload runtime settings
    try:
        settings.reload()
        swarm.update_settings()
    except Exception as e:
        logger.error(f"Error reloading settings: {e}")
        return {"status": "error", "message": "Saved .env but failed to reload runtime settings."}

    return {"status": "success", "message": "Configuration updated."}

# Mount static files
app.mount("/", StaticFiles(directory="opencore/interface/static", html=True), name="static")
