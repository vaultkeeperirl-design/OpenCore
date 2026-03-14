import os
import logging
import json

logger = logging.getLogger(__name__)

try:
    from google_auth_oauthlib.flow import Flow
except ImportError:
    Flow = None
    logger.warning("google-auth-oauthlib not installed. Google OAuth will be disabled.")


class GoogleAuthService:
    SCOPES = [
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/generative-language",
        "openid",
        "email"
    ]

    def get_login_url(self) -> str:
        """
        Initiates the Google OAuth flow and returns the authorization URL.
        """
        from opencore.config import settings

        if Flow is None:
            raise RuntimeError("Google OAuth library not installed. Please install 'google-auth-oauthlib'.")

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError("Missing Google Client ID/Secret in settings. Please configure them first.")

        client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            }
        }

        redirect_uri = f"http://{settings.host}:{settings.port}/auth/google/callback"

        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )

        auth_url, _ = flow.authorization_url(
            access_type="offline",
            prompt="consent",
            include_granted_scopes="true"
        )
        return auth_url

    def handle_callback(self, code: str) -> None:
        """
        Handles the Google OAuth callback and updates configuration.
        """
        from opencore.config import settings

        if Flow is None:
            raise RuntimeError("Google OAuth library not installed.")

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

        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )

        # Allow HTTP for local testing
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        flow.fetch_token(code=code)
        credentials = flow.credentials

        if not credentials.refresh_token:
            logger.warning("No refresh token received. User might need to revoke access to get a new one.")

        updates = {}
        if credentials.refresh_token:
            updates["GOOGLE_REFRESH_TOKEN"] = credentials.refresh_token

        if updates:
            settings.update_env(updates)

def get_google_credentials_status():
    """
    Checks for standard Application Default Credentials (ADC) locations.
    """
    try:
        # Check for OAuth refresh token
        if os.getenv("GOOGLE_REFRESH_TOKEN"):
            logger.info("Found Google OAuth Refresh Token in ENV")
            return True

        # Standard locations
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if os.path.exists(path):
                logger.info(f"Found Google ADC via ENV: {path}")
                return True

        # Check default paths
        home = os.path.expanduser("~")

        # Linux/macOS
        adc_path = os.path.join(home, ".config", "gcloud", "application_default_credentials.json")
        if os.path.exists(adc_path):
            logger.info(f"Found Google ADC at standard path: {adc_path}")
            return True

        # Windows (APPDATA)
        if os.name == 'nt':
            appdata = os.getenv("APPDATA")
            if appdata:
                win_path = os.path.join(appdata, "gcloud", "application_default_credentials.json")
                if os.path.exists(win_path):
                    logger.info(f"Found Google ADC at Windows path: {win_path}")
                    return True

        return False

    except Exception as e:
        logger.warning(f"Error checking Google credentials: {e}")
        return False
