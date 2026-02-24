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
        # Verify result message contains success and model
        self.assertTrue("Agent 'Worker' created successfully" in result)
        self.assertTrue("gpt-4o" in result)

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

    def test_create_team(self):
        swarm = Swarm("Manager")

        # 1. Verify Manager has create_team tool
        manager = swarm.get_agent("Manager")
        self.assertIn("create_team", manager.tools)

        # 2. Create a team
        result = swarm.create_team(
            name="Frontend",
            goal="Build a login page",
            lead_role="Tech Lead",
            lead_instructions="Hire a designer and a coder."
        )
        self.assertIn("Team 'Frontend' created", result)

        # 3. Verify Team Lead exists
        lead_name = "Frontend_Lead"
        self.assertIn(lead_name, swarm.agents)
        lead = swarm.agents[lead_name]

        # 4. Verify Lead prompts
        self.assertIn("Tech Lead", lead.role)
        self.assertIn("Build a login page", lead.system_prompt)

        # 5. Verify Team registry
        self.assertIn("Frontend", swarm.teams)
        self.assertIn(lead_name, swarm.teams["Frontend"])

        # 6. Verify Lead does NOT have create_team tool (since only Manager gets it)
        self.assertNotIn("create_team", lead.tools)

        # 7. Verify Lead HAS create_agent tool
        self.assertIn("create_agent", lead.tools)

    def test_list_agents_shows_teams(self):
        swarm = Swarm("Manager")
        swarm.create_team("Backend", "API", "Lead", "Go")

        manager = swarm.get_agent("Manager")
        list_tool = manager.tools["list_agents"]
        output = list_tool()

        self.assertIn("Backend", output)
        self.assertIn("Backend_Lead", output)

if __name__ == "__main__":
    unittest.main()
