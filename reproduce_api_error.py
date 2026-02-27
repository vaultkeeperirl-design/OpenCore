import requests
import sys

def test_error_format():
    url = "http://127.0.0.1:8000/agents/nonexistent_agent_123"
    print(f"Testing DELETE {url}...")
    try:
        response = requests.delete(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        data = response.json()
        if "error" in data and "code" in data["error"]:
            print("SUCCESS: Response matches ErrorResponse format.")
        elif "detail" in data:
            print("FAILURE: Response uses default FastAPI format (expected ErrorResponse).")
            sys.exit(1)
        else:
            print("UNKNOWN: Unexpected response format.")
            sys.exit(1)

    except Exception as e:
        print(f"Error making request: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_error_format()
