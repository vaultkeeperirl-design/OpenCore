import os
import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import json
from opencore.config import settings

from opencore.auth.google import GoogleAuthService

# Setup logger
logger = logging.getLogger("opencore.auth")

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
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Error initiating Google Login: {e}")
        return {"status": "error", "message": str(e)}

@auth_router.get("/google/callback")
def google_callback(request: Request):
    """
    Handles the Google OAuth callback.
    """
    code = request.query_params.get("code")
    error = request.query_params.get("error")

    if error:
         return {"status": "error", "message": f"Google Auth Error: {error}"}

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    try:
        google_auth_service.handle_callback(code=code)
        return RedirectResponse(url="/?auth_success=true")
    except (RuntimeError, ValueError) as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return {"status": "error", "message": f"Authentication failed: {str(e)}"}

@auth_router.get("/qwen/login")
def qwen_login(request: Request):
    """
    Initiates the Qwen/DashScope authentication.
    DashScope uses API keys, so we can redirect them to the DashScope console to get a key.
    """
    return RedirectResponse(url="https://dashscope.console.aliyun.com/apiKey")

@auth_router.post("/qwen/callback")
async def qwen_callback(request: Request):
    """
    Receives the API key from the frontend and saves it.
    """
    data = await request.json()
    api_key = data.get("apiKey")

    if not api_key:
        raise HTTPException(status_code=400, detail="API Key is required")

    return {"status": "success", "message": "Please copy your API key and paste it in the configuration."}
