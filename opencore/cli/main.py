import argparse
import sys
import os
import uvicorn
from opencore.cli.onboard import run_onboarding

def main():
    parser = argparse.ArgumentParser(description="OpenCore CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # onboard command
    subparsers.add_parser("onboard", help="Run the onboarding wizard to configure the environment")

    # start command
    start_parser = subparsers.add_parser("start", help="Start the OpenCore server")
    start_parser.add_argument("--host", default=None, help="Host to bind (default: 127.0.0.1 or from .env)")
    start_parser.add_argument("--port", type=int, default=None, help="Port to listen (default: 8000 or from .env)")
    start_parser.add_argument("--reload", action="store_true", help="Enable auto-reload (default: from .env)")

    args = parser.parse_args()

    if args.command == "onboard":
        run_onboarding()
    elif args.command == "start":
        # Check for .env before importing config if possible, or handle missing config gracefully
        if not os.path.exists(".env"):
            print("No .env file found.")
            choice = input("Would you like to run the OpenCore Onboarding? (y/n) [default: y]: ").strip().lower()
            if choice in ["", "y", "yes"]:
                run_onboarding()
                # Reload config module to pick up new env vars if it was already imported
                if 'opencore.config' in sys.modules:
                    import importlib
                    import opencore.config
                    importlib.reload(opencore.config)
            else:
                print("Running with default settings (or environment variables).")

        # Import config after potential onboarding
        try:
            from opencore.config import settings
        except ImportError:
            # Fallback if config fails to load due to missing env vars (though settings usually has defaults)
            print("Warning: Could not load settings from opencore.config. Using defaults.")
            class MockSettings:
                host = "127.0.0.1"
                port = 8000
                is_dev = False
            settings = MockSettings()

        host = args.host if args.host else settings.host
        port = args.port if args.port else settings.port
        reload = args.reload or settings.is_dev

        uvicorn.run(
            "opencore.interface.api:app",
            host=host,
            port=port,
            reload=reload
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
