import os
import logging
import json

logger = logging.getLogger(__name__)

def get_google_credentials_status():
    """
    Checks for standard Application Default Credentials (ADC) locations.
    """
    try:
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
