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
        print("Error: 'git' command not found. Please install git.")
        sys.exit(1)

    # Check if we are in a git repository
    if not (repo_root / ".git").exists():
        print("Error: This installation of OpenCore does not appear to be a git repository.")
        print("The 'update' command only works for git-based installations (e.g., cloned from GitHub).")
        sys.exit(1)

    print(f"Updating OpenCore from {repo_root}...")

    try:
        # Clean up build artifacts that might cause conflicts
        # specifically opencore.egg-info which is often modified by pip install -e .
        if (repo_root / "opencore.egg-info").exists():
            print(">> Cleaning build artifacts...")
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
        print(">> Pulling latest changes from git...")
        subprocess.check_call(["git", "pull"], cwd=repo_root)

        # Run pip install -e .
        # Use sys.executable to ensure we use the same python environment
        print(">> Updating dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."], cwd=repo_root)

        print("\nSuccessfully updated OpenCore.")
        print("Please restart the application to apply changes.")

    except subprocess.CalledProcessError as e:
        print(f"\nError during update: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
