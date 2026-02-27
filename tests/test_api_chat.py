import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from opencore.interface.api import app

client = TestClient(app)

class TestApiChat(unittest.TestCase):
    @patch("opencore.core.swarm.Swarm.chat")
    def test_chat_attachment_size_limit(self, mock_chat):
        # Create a large attachment (Base64 string > 15MB)
        # 15MB = 15 * 1024 * 1024 bytes = 15,728,640 bytes
        # Let's create a string slightly larger than that.
        large_content = "a" * (15 * 1024 * 1024 + 100)

        payload = {
            "message": "Test message",
            "attachments": [
                {
                    "name": "large_file.txt",
                    "type": "text/plain",
                    "content": large_content
                }
            ]
        }

        response = client.post("/chat", json=payload)

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json(), {
            "error": {
                "code": "HTTP_413",
                "message": "File too large",
                "details": None
            }
        })

        # Ensure swarm.chat was NOT called
        mock_chat.assert_not_called()

    @patch("opencore.core.swarm.Swarm.chat")
    def test_chat_attachment_within_limit(self, mock_chat):
        mock_chat.return_value = "Mock response"

        # Create a small attachment
        small_content = "a" * 100

        payload = {
            "message": "Test message",
            "attachments": [
                {
                    "name": "small_file.txt",
                    "type": "text/plain",
                    "content": small_content
                }
            ]
        }

        response = client.post("/chat", json=payload)

        self.assertEqual(response.status_code, 200)
        mock_chat.assert_called_once()

if __name__ == "__main__":
    unittest.main()
