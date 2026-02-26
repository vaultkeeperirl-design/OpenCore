import unittest
from unittest.mock import MagicMock, patch
from opencore.core.agent import Agent
from opencore.core.swarm import Swarm
from opencore.config import settings
from fastapi.testclient import TestClient
from opencore.interface.api import app, swarm
from opencore.core.exceptions import AgentNotFoundError, AgentOperationError
import os

class TestAgentManagement(unittest.TestCase):

    def setUp(self):
        self.swarm = swarm # Use the swarm instance from api.py for API tests
        self.client = TestClient(app)
        # Reset settings
        settings.max_turns = 10
        # Clear agents
        self.swarm.agents.clear()
        self.swarm.teams.clear()
        # Re-create main agent
        self.swarm.create_agent("Manager", "Manager", "System Manager")

    def test_max_turns_config(self):
        # Test default max_turns
        agent = Agent("TestBot", "Tester", "Just testing")
        # Mock provider to avoid actual LLM calls
        with patch("opencore.core.agent.get_llm_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_get_provider.return_value = mock_provider

            # Case 1: max_turns passed explicitly
            # We mock _prune_messages to avoid side effects
            agent._prune_messages = MagicMock()

            # Since think calls itself recursively, we need to be careful.
            # But here we just want to see if it starts with the right value?
            # Or checks the limit.

            # If we call think(0), it should return Error.
            result = agent.think(max_turns=0)
            self.assertEqual(result, "Error: Max turns reached.")

            # If we call think(None), it should use settings.max_turns
            # If settings.max_turns is 0 (just to test), it should error.
            settings.max_turns = 0
            result = agent.think()
            self.assertEqual(result, "Error: Max turns reached.")

    def test_agent_status_toggle(self):
        # Create an agent
        self.swarm.create_agent("Worker1", "Worker", "Work hard")
        agent = self.swarm.get_agent("Worker1")
        self.assertEqual(agent.status, "active")

        # Toggle to inactive
        result = self.swarm.toggle_agent("Worker1")
        self.assertIn("deactivated", result)
        self.assertEqual(agent.status, "inactive")

        # Verify inactive agent refuses to think
        think_result = agent.think()
        self.assertIn("inactive", think_result)

        # Toggle back to active
        result = self.swarm.toggle_agent("Worker1")
        self.assertIn("activated", result)
        self.assertEqual(agent.status, "active")

    def test_remove_agent(self):
        self.swarm.create_agent("Worker2", "Worker", "Work harder")
        self.assertIn("Worker2", self.swarm.agents)

        # Remove agent - now returns None (void) instead of string
        result = self.swarm.remove_agent("Worker2")
        self.assertIsNone(result)
        self.assertNotIn("Worker2", self.swarm.agents)

        # Try removing non-existent - should raise AgentNotFoundError
        with self.assertRaises(AgentNotFoundError):
            self.swarm.remove_agent("Worker2")

        # Try removing Manager - should raise AgentOperationError
        with self.assertRaises(AgentOperationError):
            self.swarm.remove_agent("Manager")

    def test_remove_team_member(self):
        # Create team
        # We need to mock create_agent because create_team calls it
        # But here we can just use the real one.
        # However, create_team calls create_agent for the lead.

        # Manually set up team
        self.swarm.create_agent("Lead1", "Lead", "Lead the team")
        self.swarm.teams["Team1"] = ["Lead1"]

        # Remove Lead1
        self.swarm.remove_agent("Lead1")
        self.assertNotIn("Lead1", self.swarm.agents)
        # Check team membership
        self.assertNotIn("Lead1", self.swarm.teams["Team1"])

    def test_api_endpoints(self):
        # Create an agent
        self.swarm.create_agent("APIWorker", "Worker", "API Test")

        # Test Toggle API
        response = self.client.post("/agents/APIWorker/toggle")
        self.assertEqual(response.status_code, 200)
        self.assertIn("deactivated", response.json()["message"])
        self.assertEqual(self.swarm.get_agent("APIWorker").status, "inactive")

        response = self.client.post("/agents/APIWorker/toggle")
        self.assertEqual(response.status_code, 200)
        self.assertIn("activated", response.json()["message"])
        self.assertEqual(self.swarm.get_agent("APIWorker").status, "active")

        # Test Delete API
        response = self.client.delete("/agents/APIWorker")
        self.assertEqual(response.status_code, 200)
        self.assertIn("removed", response.json()["message"])
        self.assertIsNone(self.swarm.get_agent("APIWorker"))

if __name__ == '__main__':
    unittest.main()
