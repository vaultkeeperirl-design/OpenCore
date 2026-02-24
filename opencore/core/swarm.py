from typing import Dict, Optional, List, Any
from opencore.core.agent import Agent
from opencore.tools.base import register_base_tools
from opencore.config import settings

class Swarm:
    def __init__(self, main_agent_name: str = "Manager", default_model: str = "gpt-4o"):
        self.agents: Dict[str, Agent] = {}
        self.teams: Dict[str, List[str]] = {}  # Map team_name -> list of agent_names
        self.main_agent_name = main_agent_name
        # Allow env var to override default model
        self.default_model = settings.llm_model or default_model

        # Create the main agent
        self.create_agent(
            name=main_agent_name,
            role="Manager",
            system_prompt="You are the central system manager. Your role is to orchestrate sub-agents and execute user directives efficiently. Respond with brevity and precision. Use system-style language (e.g., 'Acknowledged', 'Initiating')."
        )

    def create_agent(self, name: str, role: str, system_prompt: str, model: Optional[str] = None) -> str:
        if name in self.agents:
            return f"Error: Agent '{name}' already exists."

        # Use passed model, or swarm default
        is_custom = model is not None
        agent_model = model if model else self.default_model

        new_agent = Agent(name, role, system_prompt, model=agent_model, is_custom_model=is_custom)
        self.agents[name] = new_agent

        # Register swarm tools for the new agent
        self._register_swarm_tools(new_agent)

        # Register base tools (filesystem, command execution)
        register_base_tools(new_agent)

        return f"Agent '{name}' created successfully using model '{agent_model}'."

    def create_team(self, name: str, goal: str, lead_role: str, lead_instructions: str) -> str:
        """
        Creates a new team with a designated leader.
        The leader is instructed to achieve the goal by creating sub-agents if necessary.
        """
        if name in self.teams:
            return f"Error: Team '{name}' already exists."

        # Create Team Lead
        lead_name = f"{name}_Lead"
        if lead_name in self.agents:
            return f"Error: Agent '{lead_name}' already exists. Cannot create team lead."

        lead_system_prompt = (
            f"You are the {lead_role} and leader of the '{name}' team. "
            f"Your primary goal is: {goal}. "
            f"Instructions: {lead_instructions} "
            "You have the authority to create new agents (workers) using 'create_agent' to help you achieve this goal. "
            "Delegate tasks effectively and report final results back."
        )

        # Create the lead agent
        # We use the swarm's default model for the lead unless specified otherwise (could be added as param)
        result = self.create_agent(lead_name, lead_role, lead_system_prompt)

        # Register team
        self.teams[name] = [lead_name]

        return f"Team '{name}' created. Leader '{lead_name}' is ready. {result}"

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

        # Tool: Create Team (Main Agent Only)
        if agent.name == self.main_agent_name:
            create_team_schema = {
                "type": "function",
                "function": {
                    "name": "create_team",
                    "description": "Creates a new team of agents led by a specialized Team Lead.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "The name of the team (e.g., 'Frontend', 'Research')."},
                            "goal": {"type": "string", "description": "The primary goal of the team."},
                            "lead_role": {"type": "string", "description": "The role of the team leader (e.g., 'Tech Lead', 'Project Manager')."},
                            "lead_instructions": {"type": "string", "description": "Specific instructions for the team leader on how to manage the team."}
                        },
                        "required": ["name", "goal", "lead_role", "lead_instructions"]
                    }
                }
            }

            def create_team_wrapper(name: str, goal: str, lead_role: str, lead_instructions: str):
                return self.create_team(name, goal, lead_role, lead_instructions)

            agent.register_tool(create_team_wrapper, create_team_schema)

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
                "description": "Lists all available agents and teams in the swarm.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }

        def list_agents_wrapper():
            agent_list = list(self.agents.keys())
            team_list = list(self.teams.keys())
            return f"Available agents: {agent_list}. Teams: {team_list}"

        agent.register_tool(list_agents_wrapper, list_agents_schema)

    def update_settings(self):
        """Reloads configuration and updates agents."""
        # Allow env var to override default model
        self.default_model = settings.llm_model or "gpt-4o"

        # Update existing agents to use the new default model if they aren't custom
        for agent in self.agents.values():
            if not getattr(agent, "is_custom_model", False):
                agent.model = self.default_model

            # Clear client to ensure new auth is picked up if needed
            agent.client = None

    def chat(self, message: str, attachments: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Entry point for the user to chat with the main agent.
        """
        main_agent = self.agents[self.main_agent_name]
        return main_agent.chat(message, attachments=attachments)
