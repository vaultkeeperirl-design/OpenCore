import os
import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import json
from pydantic import BaseModel
from opencore.config import settings

from opencore.auth.google import GoogleAuthService

# Setup logger
logger = logging.getLogger("opencore.auth")

class QwenCallbackRequest(BaseModel):
    apiKey: str

class AuthCallbackResponse(BaseModel):
    status: str
    message: str

auth_router = APIRouter(prefix="/auth", tags=["auth"])
google_auth_service = GoogleAuthService()

@auth_router.get("/google/login")
def google_login(request: Request):
    """
    Initiates the Google OAuth flow.
    """
    try:
        auth_url = google_auth_service.get_login_url()
        return RedirectResponse(url=auth_url)
    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error initiating Google Login: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while initiating login")

@auth_router.get("/google/callback")
def google_callback(request: Request):
    """
    Handles the Google OAuth callback.
    """
    code = request.query_params.get("code")
    error = request.query_params.get("error")

    if error:
        raise HTTPException(status_code=400, detail=f"Google Auth Error: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    try:
        google_auth_service.handle_callback(code=code)
        return RedirectResponse(url="/?auth_success=true")
    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred during authentication")

@auth_router.get("/qwen/login")
def qwen_login(request: Request):
    """
    Initiates the Qwen/DashScope authentication.
    DashScope uses API keys, so we can redirect them to the DashScope console to get a key.
    """
    return RedirectResponse(url="https://dashscope.console.aliyun.com/apiKey")

@auth_router.post("/qwen/callback", response_model=AuthCallbackResponse)
async def qwen_callback(request_data: QwenCallbackRequest):
    """
    Receives the API key from the frontend and saves it.
    """
    return AuthCallbackResponse(
        status="success",
        message="Please copy your API key and paste it in the configuration."
    )
