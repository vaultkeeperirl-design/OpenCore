import os
import sys
import subprocess
from pathlib import Path

def update_system():
    # Assume we are in opencore/cli/update.py
    # Repo root is 3 levels up
    repo_root = Path(__file__).resolve().parent.parent.parent

    # Check if git is installed
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("CRITICAL ERROR: GIT PROTOCOL NOT FOUND. INSTALLATION REQUIRED.")
        sys.exit(1)

    # Check if we are in a git repository
    if not (repo_root / ".git").exists():
        print("CRITICAL ERROR: REPOSITORY INTEGRITY CHECK FAILED.")
        print("SYSTEM UPDATE REQUIRES GIT-BASED INSTALLATION.")
        sys.exit(1)

    print(f"\n--- OPENCORE // SYSTEM UPDATE SEQUENCE ---\nTARGET ROOT: {repo_root}")

    try:
        # Clean up build artifacts that might cause conflicts
        # specifically opencore.egg-info which is often modified by pip install -e .
        if (repo_root / "opencore.egg-info").exists():
            print(">> PURGING CACHED ARTIFACTS...")
            try:
                subprocess.run(
                    ["git", "checkout", "HEAD", "--", "opencore.egg-info"],
                    cwd=repo_root,
                    check=False,  # Don't fail if it doesn't exist in HEAD or other minor issues
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass  # Best effort cleanup

        # Run git pull
        print(">> SYNCING REPOSITORY DATA...")
        subprocess.check_call(["git", "pull"], cwd=repo_root)

        # Run pip install -e .
        # Use sys.executable to ensure we use the same python environment
        print(">> INSTALLING NEURAL DEPENDENCIES...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."], cwd=repo_root)

        print("\n>> UPDATE COMPLETE. SYSTEM REVISION APPLIED.")
        print("ACTION REQUIRED: RESTART SYSTEM TO INITIALIZE NEW PROTOCOLS.")

    except subprocess.CalledProcessError as e:
        print(f"\n[UPDATE FAILED]: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[UNEXPECTED SYSTEM ERROR]: {e}")
        sys.exit(1)
