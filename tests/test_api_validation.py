import unittest
import json
from fastapi.testclient import TestClient
from opencore.interface.api import app

class TestLargePayload(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_large_attachment(self):
        # Create a payload > 15MB
        # 15MB = 15 * 1024 * 1024 bytes = 15728640 bytes
        # Base64 string of 16MB
        large_content = "a" * (16 * 1024 * 1024)

        payload = {
            "message": "Test large file",
            "attachments": [
                {
                    "name": "large.txt",
                    "type": "text/plain",
                    "content": large_content
                }
            ]
        }

        response = self.client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json(), {
            "error": {
                "code": "HTTP_413",
                "message": "File too large",
                "details": None
            }
        })

if __name__ == '__main__':
    unittest.main()
