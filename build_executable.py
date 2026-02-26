import PyInstaller.__main__
import platform
import os
import sys

def build():
    print("Starting PyInstaller build...")

    # Determine OS separator for --add-data
    if platform.system() == "Windows":
        sep = ";"
    else:
        sep = ":"

    # Define paths
    # We assume the script is run from the repo root
    # opencore/interface/static
    static_src = os.path.join("opencore", "interface", "static")

    # Destination inside the bundle should preserve structure
    # opencore/interface/static
    static_dest = os.path.join("opencore", "interface", "static")

    # Verify static source exists
    if not os.path.exists(static_src):
        print(f"Warning: Static folder '{static_src}' does not exist.")
        # Ensure directory exists so PyInstaller doesn't fail
        os.makedirs(static_src, exist_ok=True)
    else:
        print(f"Found static assets in '{static_src}'.")

    # Construct --add-data argument
    add_data_arg = f"{static_src}{sep}{static_dest}"

    # Hidden imports required for Uvicorn and other dynamic loaders
    hidden_imports = [
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.lifespan.on",
        "engineio.async_drivers.asgi",
        "boto3",
        "botocore",
        "python_multipart",
    ]

    # Construct arguments list
    args = [
        "opencore/cli/main.py",     # Entry script
        "--name=opencore",          # Executable name
        "--onefile",                # Single executable
        "--clean",                  # Clean cache
        f"--add-data={add_data_arg}",
    ]

    # Add hidden imports
    for imp in hidden_imports:
        args.append(f"--hidden-import={imp}")

    print(f"Running PyInstaller with arguments: {args}")

    # Run PyInstaller
    PyInstaller.__main__.run(args)

    print("Build process completed.")

    # Check if dist folder exists and list content
    dist_dir = "dist"
    if os.path.exists(dist_dir):
        print(f"Artifacts in '{dist_dir}':")
        for f in os.listdir(dist_dir):
            print(f" - {f}")

if __name__ == "__main__":
    build()
