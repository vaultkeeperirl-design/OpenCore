import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from opencore.interface.api import app
import os

class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        # raise_server_exceptions=False ensures that exceptions are handled by the app's exception handlers
        self.client = TestClient(app, raise_server_exceptions=False)

    @patch("opencore.interface.api.swarm")
    def test_generic_exception_development(self, mock_swarm):
        # Setup mock to raise an exception
        mock_swarm.chat.side_effect = Exception("Something went wrong!")

        # Make request with APP_ENV=development
        with patch.dict(os.environ, {"APP_ENV": "development"}):
            response = self.client.post("/chat", json={"message": "Hello"})

        # Assert status code
        self.assertEqual(response.status_code, 500)

        # Assert response structure
        json_data = response.json()
        self.assertIn("error", json_data)
        self.assertEqual(json_data["error"]["code"], "INTERNAL_SERVER_ERROR")
        self.assertEqual(json_data["error"]["message"], "An unexpected error occurred.")
        self.assertIn("details", json_data["error"])
        self.assertIn("Something went wrong!", json_data["error"]["details"])

    @patch("opencore.interface.api.swarm")
    def test_generic_exception_production(self, mock_swarm):
        # Setup mock to raise an exception
        mock_swarm.chat.side_effect = Exception("Secret info leaked!")

        # Make request with APP_ENV=production
        with patch.dict(os.environ, {"APP_ENV": "production"}):
            response = self.client.post("/chat", json={"message": "Hello"})

        # Assert status code
        self.assertEqual(response.status_code, 500)

        # Assert response structure
        json_data = response.json()
        self.assertIn("error", json_data)
        self.assertEqual(json_data["error"]["code"], "INTERNAL_SERVER_ERROR")
        self.assertEqual(json_data["error"]["message"], "An unexpected error occurred.")

        # Ensure details is None
        self.assertIsNone(json_data["error"]["details"])

    @patch("opencore.interface.api.swarm")
    def test_successful_request(self, mock_swarm):
        # Setup mock to return success
        mock_swarm.chat.return_value = "Hello from swarm"
        # swarm.agents is a dict, keys() is called
        mock_swarm.agents = {"Manager": "agent_obj"}

        # Make request
        response = self.client.post("/chat", json={"message": "Hello"})

        # Assert status code
        self.assertEqual(response.status_code, 200)

        # Assert structure
        json_data = response.json()
        self.assertEqual(json_data["response"], "Hello from swarm")
        self.assertEqual(json_data["agents"], ["Manager"])
