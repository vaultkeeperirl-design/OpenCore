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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = swarm.chat(request.message)
        return ChatResponse(
            response=response,
            agents=list(swarm.agents.keys())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def get_agents():
    return {"agents": list(swarm.agents.keys())}

# Mount static files
app.mount("/", StaticFiles(directory="opencore/interface/static", html=True), name="static")
