import os
from opencore.tools.base import read_file, list_files, _is_safe_path

# Create a dummy .env file if it doesn't exist
if not os.path.exists(".env"):
    with open(".env", "w") as f:
        f.write("SECRET=12345")

# Test 1: Check if _is_safe_path allows .env
print(f"Is .env safe? {_is_safe_path('.env')}")

# Test 2: Try to read .env
content = read_file(".env")
print(f"Read .env content: {content}")

# Test 3: List files - check if .env is visible
files = list_files(".")
if ".env" in files:
    print(".env is visible in list_files")
else:
    print(".env is NOT visible in list_files")

# Cleanup
# os.remove(".env")
