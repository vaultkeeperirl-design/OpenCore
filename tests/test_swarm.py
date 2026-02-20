import unittest
from unittest.mock import MagicMock
from opencore.core.swarm import Swarm

class TestSwarm(unittest.TestCase):
    def test_swarm_initialization(self):
        swarm = Swarm("Boss")
        self.assertIn("Boss", swarm.agents)
        self.assertEqual(swarm.agents["Boss"].role, "Manager")

    def test_create_agent(self):
        swarm = Swarm("Boss")
        result = swarm.create_agent("Worker", "Coder", "Write code.")
        self.assertIn("Worker", swarm.agents)
        self.assertEqual(result, "Agent 'Worker' created successfully.")

        # Verify worker has tools
        worker = swarm.agents["Worker"]
        self.assertIn("delegate_task", worker.tools)

    def test_delegate_task_mock(self):
        swarm = Swarm("Boss")
        boss = swarm.agents["Boss"]

        # Create a worker manually
        worker = MagicMock()
        worker.chat.return_value = "Task done."
        swarm.agents["Worker"] = worker

        # Simulate boss delegating
        # We need to manually call the tool wrapper since we can't easily access the closure.
        # But we can access it via boss.tools["delegate_task"]

        delegate_func = boss.tools["delegate_task"]
        response = delegate_func("Worker", "Do X")

        self.assertEqual(response, "Response from Worker: Task done.")
        worker.chat.assert_called()

if __name__ == "__main__":
    unittest.main()
