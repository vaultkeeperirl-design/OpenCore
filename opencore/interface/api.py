from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from opencore.core.swarm import Swarm
import os

app = FastAPI()

# Initialize Swarm
swarm = Swarm()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    agents: list
    tool_logs: list = [] # Future: detailed logs

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # In a real streaming scenario, we would use Server-Sent Events (SSE) or WebSockets.
        # For this MVP, we block and return the final response, but the frontend shows a loading state.

        # We could potentially capture logs here by inspecting the agent's recent messages
        # but the current `think` method returns just the string.

        response = swarm.chat(request.message)

        return ChatResponse(
            response=response,
            agents=list(swarm.agents.keys())
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def get_agents():
    return {"agents": list(swarm.agents.keys())}

# Mount static files
app.mount("/", StaticFiles(directory="opencore/interface/static", html=True), name="static")
