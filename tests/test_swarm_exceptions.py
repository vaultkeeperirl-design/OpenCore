import unittest
from unittest.mock import MagicMock
from opencore.core.swarm import Swarm
from opencore.core.exceptions import AgentNotFoundError, AgentOperationError

class TestSwarmExceptions(unittest.TestCase):
    def setUp(self):
        self.swarm = Swarm("Manager")
        self.swarm.create_agent("Worker", "Role", "Prompt")

    def test_remove_agent_success(self):
        # Should return None (void) on success
        result = self.swarm.remove_agent("Worker")
        self.assertIsNone(result)
        self.assertNotIn("Worker", self.swarm.agents)

    def test_remove_agent_not_found(self):
        with self.assertRaises(AgentNotFoundError):
            self.swarm.remove_agent("NonExistent")

    def test_remove_main_agent_error(self):
        with self.assertRaises(AgentOperationError):
            self.swarm.remove_agent("Manager")

    def test_toggle_agent_success(self):
        # Starts active
        status_msg = self.swarm.toggle_agent("Worker")
        self.assertIn("deactivated", status_msg)
        self.assertEqual(self.swarm.agents["Worker"].status, "inactive")

        status_msg = self.swarm.toggle_agent("Worker")
        self.assertIn("activated", status_msg)
        self.assertEqual(self.swarm.agents["Worker"].status, "active")

    def test_toggle_agent_not_found(self):
        with self.assertRaises(AgentNotFoundError):
            self.swarm.toggle_agent("NonExistent")

    def test_toggle_main_agent_error(self):
        with self.assertRaises(AgentOperationError):
            self.swarm.toggle_agent("Manager")

    def test_tool_wrappers_return_strings(self):
        """
        Verify that the tool wrappers (used by LLMs) catch exceptions
        and return error strings instead of raising.
        """
        manager = self.swarm.get_agent("Manager")

        # remove_agent wrapper
        remove_tool = manager.tools["remove_agent"]

        # Test wrapper success
        res = remove_tool("Worker")
        self.assertIn("removed", res)

        # Test wrapper failure (not found)
        res = remove_tool("NonExistent")
        self.assertTrue(res.startswith("Error:"))

        # Test wrapper failure (main agent)
        res = remove_tool("Manager")
        self.assertTrue(res.startswith("Error:"))

        # toggle_agent wrapper
        toggle_tool = manager.tools["toggle_agent"]

        # Test wrapper failure (not found)
        res = toggle_tool("NonExistent")
        self.assertTrue(res.startswith("Error:"))

if __name__ == "__main__":
    unittest.main()
