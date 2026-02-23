from opencore.auth.qwen import get_qwen_credentials
from opencore.auth.google import get_google_credentials_status

def get_auth_status():
    """
    Returns a dictionary of provider authentication status.
    """
    return {
        "google": get_google_credentials_status(),
        "qwen": bool(get_qwen_credentials())
    }
