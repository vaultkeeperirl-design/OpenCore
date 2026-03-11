import subprocess
import sys

def main():
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/"], env={"PYTHONPATH": "."}, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
