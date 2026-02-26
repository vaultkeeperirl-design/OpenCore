import unittest
from fastapi.testclient import TestClient
from opencore.interface.api import app

class TestMalformedAttachment(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_malformed_attachment(self):
        """
        Sends a request with an attachment missing 'name' and 'type'.
        Expects a 422 Unprocessable Entity because of Pydantic validation.
        """
        payload = {
            "message": "Test malformed attachment",
            "attachments": [
                {
                    "content": "some content"
                    # Missing 'name' and 'type'
                }
            ]
        }

        response = self.client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 422)

        # Verify that the error detail mentions the missing fields
        # Note: Pydantic v2 error format is slightly different but contains location info
        self.assertIn("attachments", str(response.json()))

if __name__ == '__main__':
    unittest.main()
