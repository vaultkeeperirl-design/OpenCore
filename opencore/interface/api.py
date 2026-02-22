from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
from opencore.core.swarm import Swarm
from opencore.interface.middleware import global_exception_handler
from opencore.core.scheduler import AsyncScheduler
from opencore.interface.heartbeat import heartbeat_manager
from opencore.config import settings
import os

# Initialize Scheduler
scheduler = AsyncScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register heartbeat job
    scheduler.add_job(
        heartbeat_manager.log_heartbeat,
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

# Initialize Swarm
swarm = Swarm()

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

# Mount static files
app.mount("/", StaticFiles(directory="opencore/interface/static", html=True), name="static")
