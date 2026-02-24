import os
import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import json
from google_auth_oauthlib.flow import Flow
from opencore.config import settings

# Setup logger
logger = logging.getLogger("opencore.auth")

auth_router = APIRouter(prefix="/auth", tags=["auth"])

# Define scopes for Vertex AI and Gemini API
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/generative-language",
    "openid",
    "email"
]

@auth_router.get("/google/login")
async def google_login(request: Request):
    """
    Initiates the Google OAuth flow.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        return {"status": "error", "message": "Missing Google Client ID/Secret in settings. Please configure them first."}

    # Construct client config dict
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        }
    }

    # Determine redirect URI based on current settings
    redirect_uri = f"http://{settings.host}:{settings.port}/auth/google/callback"

    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )

        auth_url, _ = flow.authorization_url(
            access_type="offline",
            prompt="consent",
            include_granted_scopes="true"
        )

        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Error initiating Google Login: {e}")
        return {"status": "error", "message": str(e)}

@auth_router.get("/google/callback")
async def google_callback(request: Request):
    """
    Handles the Google OAuth callback.
    """
    code = request.query_params.get("code")
    error = request.query_params.get("error")

    if error:
         return {"status": "error", "message": f"Google Auth Error: {error}"}

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = f"http://{settings.host}:{settings.port}/auth/google/callback"

    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        }
    }

    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )

        # Allow HTTP for local testing
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        flow.fetch_token(code=code)
        credentials = flow.credentials

        if not credentials.refresh_token:
            logger.warning("No refresh token received. User might need to revoke access to get a new one.")
            # We can still proceed with access token, but it will expire.
            # Ideally we want refresh token.
            pass

        # Save to settings
        updates = {}
        if credentials.refresh_token:
            updates["GOOGLE_REFRESH_TOKEN"] = credentials.refresh_token

        # We might also want to save default project if available?
        # But for now, just the token.

        if updates:
            settings.update_env(updates)

        return RedirectResponse(url="/?auth_success=true")

    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return {"status": "error", "message": f"Authentication failed: {str(e)}"}

@auth_router.get("/qwen/login")
async def qwen_login(request: Request):
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
