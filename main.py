import uvicorn
import os
import sys

# Check for .env before loading config
if not os.path.exists(".env"):
    print("No .env file found.")
    run_onboard = input("Would you like to run the OpenCore Onboarding? (y/n) [default: y]: ").strip().lower()
    if run_onboard in ["", "y", "yes"]:
        from opencore.cli.onboard import run_onboarding
        run_onboarding()
        # Reload config module to pick up new env vars if it was already imported
        if 'opencore.config' in sys.modules:
            import importlib
            import opencore.config
            importlib.reload(opencore.config)
    else:
        print("Running with default settings (or environment variables).")

from opencore.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "opencore.interface.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_dev
    )
