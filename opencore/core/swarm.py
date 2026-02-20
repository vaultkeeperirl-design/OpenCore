from typing import Dict, Optional, Any
from opencore.core.agent import Agent
from opencore.tools.base import register_base_tools

class Swarm:
    def __init__(self, main_agent_name: str = "Manager"):
        self.agents: Dict[str, Agent] = {}
        self.main_agent_name = main_agent_name

        # Create the main agent
        self.create_agent(
            name=main_agent_name,
            role="Manager",
            system_prompt="You are the main manager of the swarm. You can create sub-agents and delegate tasks to them."
        )

    def create_agent(self, name: str, role: str, system_prompt: str) -> str:
        if name in self.agents:
            return f"Error: Agent '{name}' already exists."

        new_agent = Agent(name, role, system_prompt)
        self.agents[name] = new_agent

        # Register swarm tools for the new agent
        self._register_swarm_tools(new_agent)

        # Register base tools (filesystem, command execution)
        register_base_tools(new_agent)

        return f"Agent '{name}' created successfully."

    def get_agent(self, name: str) -> Optional[Agent]:
        return self.agents.get(name)

    def _register_swarm_tools(self, agent: Agent):
        # Tool: Create Agent
        create_agent_schema = {
            "type": "function",
            "function": {
                "name": "create_agent",
                "description": "Creates a new agent with a specific role and instructions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "The name of the new agent."},
                        "role": {"type": "string", "description": "The role of the new agent (e.g., 'Coder', 'Researcher')."},
                        "instructions": {"type": "string", "description": "Specific system instructions for the agent."}
                    },
                    "required": ["name", "role", "instructions"]
                }
            }
        }

        def create_agent_wrapper(name: str, role: str, instructions: str):
            return self.create_agent(name, role, instructions)

        agent.register_tool(create_agent_wrapper, create_agent_schema)

        # Tool: Delegate Task
        delegate_schema = {
            "type": "function",
            "function": {
                "name": "delegate_task",
                "description": "Delegates a task to another existing agent and waits for the result.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to_agent": {"type": "string", "description": "The name of the agent to delegate to."},
                        "task": {"type": "string", "description": "The task description or message."}
                    },
                    "required": ["to_agent", "task"]
                }
            }
        }

        def delegate_task_wrapper(to_agent: str, task: str):
            target_agent = self.get_agent(to_agent)
            if not target_agent:
                return f"Error: Agent '{to_agent}' not found. Available agents: {list(self.agents.keys())}"

            # We add the sender's context implicitly by just chatting with the target
            # In a more complex system, we'd pass the sender's name.
            response = target_agent.chat(f"Request from {agent.name}: {task}")
            return f"Response from {to_agent}: {response}"

        agent.register_tool(delegate_task_wrapper, delegate_schema)

        # Tool: List Agents
        list_agents_schema = {
            "type": "function",
            "function": {
                "name": "list_agents",
                "description": "Lists all available agents in the swarm.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }

        def list_agents_wrapper():
            return f"Available agents: {list(self.agents.keys())}"

        agent.register_tool(list_agents_wrapper, list_agents_schema)

    def chat(self, message: str) -> str:
        """
        Entry point for the user to chat with the main agent.
        """
        main_agent = self.agents[self.main_agent_name]
        return main_agent.chat(message)
