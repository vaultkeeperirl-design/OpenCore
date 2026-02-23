import json
import os
import logging

logger = logging.getLogger(__name__)

def get_qwen_credentials():
    """
    Checks for ~/.qwen/oauth_creds.json and returns the access_token if present.
    """
    try:
        home = os.path.expanduser("~")
        creds_path = os.path.join(home, ".qwen", "oauth_creds.json")

        if os.path.exists(creds_path):
            with open(creds_path, "r") as f:
                creds = json.load(f)
                token = creds.get("access_token")
                if token:
                    logger.info("Found Qwen OAuth credentials.")
                    return token
        return None
    except Exception as e:
        logger.warning(f"Error checking Qwen credentials: {e}")
        return None
