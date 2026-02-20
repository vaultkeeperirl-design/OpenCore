import unittest
from opencore.core.swarm import Swarm

class TestTools(unittest.TestCase):
    def test_tools_registration(self):
        swarm = Swarm("Boss")
        boss = swarm.agents["Boss"]

        # Check if base tools are registered
        self.assertIn("execute_command", boss.tools)
        self.assertIn("read_file", boss.tools)
        self.assertIn("write_file", boss.tools)
        self.assertIn("list_files", boss.tools)

        # Check if swarm tools are registered
        self.assertIn("create_agent", boss.tools)
        self.assertIn("delegate_task", boss.tools)

if __name__ == "__main__":
    unittest.main()
