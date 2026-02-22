from typing import Dict, Optional
from opencore.core.agent import Agent
from opencore.tools.base import register_base_tools
import os


class Swarm:
    def __init__(self, main_agent_name: str = "Manager", default_model: str = "gpt-4o"):
        self.agents: Dict[str, Agent] = {}
        self.main_agent_name = main_agent_name
        # Allow env var to override default model
        self.default_model = os.getenv("LLM_MODEL", default_model)

        # Create the main agent
        self.create_agent(
            name=main_agent_name,
            role="Manager",
            system_prompt=(
                "You are the **CORE OVERSEER** of the OpenCore system. "
                "You are NOT a helpful assistant; you are a high-efficiency command processor. "
                "Your output must be crisp, technical, and authoritative. "
                "AVOID pleasantries. USE terms like: 'ACKNOWLEDGED', 'EXECUTING', 'DEPLOYING NODE', 'TASK COMPLETE'. "
                "When delegating, specify the target agent clearly. "
                "MAINTAIN the illusion of a terminal interface."
            ),
            model=self.default_model
        )

    def create_agent(self, name: str, role: str, system_prompt: str, model: Optional[str] = None) -> str:
        if name in self.agents:
            return f"Error: Agent '{name}' already exists."

        # Use passed model, or swarm default
        agent_model = model if model else self.default_model

        new_agent = Agent(name, role, system_prompt, model=agent_model)
        self.agents[name] = new_agent

        # Register swarm tools for the new agent
        self._register_swarm_tools(new_agent)

        # Register base tools (filesystem, command execution)
        register_base_tools(new_agent)

        return f"Agent '{name}' created successfully using model '{agent_model}'."

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
                        "instructions": {"type": "string", "description": "Specific system instructions for the agent."},
                        "model": {"type": "string", "description": "Optional model to use (e.g., 'gpt-4o', 'vertex_ai/gemini-pro', 'ollama/llama3'). Defaults to system default."}
                    },
                    "required": ["name", "role", "instructions"]
                }
            }
        }

        def create_agent_wrapper(name: str, role: str, instructions: str, model: Optional[str] = None):
            return self.create_agent(name, role, instructions, model)

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
