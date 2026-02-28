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

        json_response = response.json()
        self.assertIn("error", json_response)
        self.assertEqual(json_response["error"]["code"], "UNPROCESSABLE_ENTITY")
        self.assertEqual(json_response["error"]["message"], "Request validation failed.")

        # Verify that the error detail mentions the missing fields
        # Note: Pydantic v2 error format is slightly different but contains location info
        self.assertIn("attachments", json_response["error"]["details"])

if __name__ == '__main__':
    unittest.main()
