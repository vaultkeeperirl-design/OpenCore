import uvicorn
import os
import sys

# Check for .env before loading config
if not os.path.exists(".env"):
    print("No .env file found. Initializing default configuration...")
    from opencore.cli.onboard import run_onboarding
    # Non-interactive mode for automated setup
    run_onboarding(interactive=False)

    # Reload config module to pick up new env vars if imported
    if 'opencore.config' in sys.modules:
        import importlib
        import opencore.config
        importlib.reload(opencore.config)
else:
    print(
        "Running with existing settings."
    )

from opencore.config import settings
from opencore.core.logging import configure_logging

if __name__ == "__main__":
    configure_logging()
    uvicorn.run(
        "opencore.interface.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_dev
    )
