from typing import Dict, Optional, List, Any
import threading
from opencore.core.agent import Agent
from opencore.tools.base import register_base_tools
from opencore.config import settings
from opencore.llm.factory import is_provider_available, get_available_model_list
from opencore.core.exceptions import AgentNotFoundError, AgentOperationError
from opencore.core.context import activity_log_ctx
import datetime


class Swarm:
    def __init__(self, main_agent_name: str = "Manager", default_model: str = "gpt-4o"):
        self._lock = threading.Lock()
        self.agents: Dict[str, Agent] = {}
        self.teams: Dict[str, List[str]] = {}  # Map team_name -> list of agent_names
        self.interactions: List[Dict[str, str]] = []  # Track recent interactions
        self.main_agent_name = main_agent_name
        # Allow env var to override default model
        self.default_model = settings.llm_model or default_model

        # Create the main agent
        self.create_agent(
            name=main_agent_name,
            role="Manager",
            system_prompt=(
                "You are the central system manager. Your role is to orchestrate sub-agents and execute user directives "
                "efficiently. Respond with brevity and precision. Use system-style language (e.g., 'Acknowledged', "
                "'Initiating')."
            )
        )

    def create_agent(
        self,
        name: str,
        role: str,
        system_prompt: str,
        model: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> str:
        with self._lock:
            if name in self.agents:
                return f"Error: Agent '{name}' already exists."

        # Validate requested model availability if provided
        if model and not is_provider_available(model):
            available = ", ".join(get_available_model_list())
            return (
                f"Error: Provider for model '{model}' is not configured. "
                f"Please configure the API key or choose from: {available}"
            )

        # Use passed model, or swarm default
        is_custom = model is not None
        agent_model = model if model else self.default_model

        new_agent = Agent(
            name, role, system_prompt, model=agent_model, is_custom_model=is_custom, created_by=created_by
        )
        with self._lock:
            self.agents[name] = new_agent

        # Register swarm tools for the new agent
        self._register_swarm_tools(new_agent)

        # Register base tools (filesystem, command execution)
        register_base_tools(new_agent)

        if name != self.main_agent_name:
            self._log_activity({
                "type": "lifecycle",
                "subtype": "create",
                "agent": name,
                "timestamp": datetime.datetime.now().isoformat()
            })

        return f"Agent '{name}' created successfully using model '{agent_model}'."

    def _log_activity(self, activity: Dict[str, Any]):
        """Helper to safely log request-scoped activity."""
        try:
            log = activity_log_ctx.get()
            if log is not None:
                log.append(activity)
        except (LookupError, NameError):
            pass

    def remove_agent(self, name: str) -> Optional[str]:
        """Removes an agent from the swarm."""
        with self._lock:
            if name not in self.agents:
                raise AgentNotFoundError(f"Agent '{name}' not found.")

            if name == self.main_agent_name:
                raise AgentOperationError("Cannot remove the main manager agent.")

            del self.agents[name]

            self._log_activity({
                "type": "lifecycle",
                "subtype": "remove",
                "agent": name,
                "timestamp": datetime.datetime.now().isoformat()
            })

            # Cleanup team references if this agent was a leader
            for team_name, members in self.teams.items():
                if name in members:
                    members.remove(name)
                # If the removed agent was the leader (usually first in list or by name convention)
                # For now, just removing from list is enough.

        return None

    def toggle_agent(self, name: str) -> str:
        """Toggles an agent's active status."""
        with self._lock:
            agent = self.agents.get(name)
            if not agent:
                raise AgentNotFoundError(f"Agent '{name}' not found.")

            if name == self.main_agent_name:
                 raise AgentOperationError("Cannot toggle the main manager agent.")

            if agent.status == "active":
                agent.status = "inactive"
                return f"Agent '{name}' deactivated."
            else:
                agent.status = "active"
                return f"Agent '{name}' activated."

    def create_team(self, name: str, goal: str, lead_role: str, lead_instructions: str) -> str:
        """
        Creates a new team with a designated leader.
        The leader is instructed to achieve the goal by creating sub-agents if necessary.
        """
        with self._lock:
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
        # The lead is created by the main agent (Manager) usually
        result = self.create_agent(lead_name, lead_role, lead_system_prompt, created_by=self.main_agent_name)

        # Register team
        with self._lock:
            self.teams[name] = [lead_name]

        return f"Team '{name}' created. Leader '{lead_name}' is ready. {result}"

    def get_agent(self, name: str) -> Optional[Agent]:
        with self._lock:
            return self.agents.get(name)

    def _register_swarm_tools(self, agent: Agent):
        # Dynamically build model description
        available_models = get_available_model_list()
        # Ensure system default is visible if valid and available
        if self.default_model and self.default_model not in available_models:
            if is_provider_available(self.default_model):
                available_models.insert(0, self.default_model)

        models_str = ", ".join(available_models) if available_models else "No external models configured"

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
                        "model": {
                            "type": "string",
                            "description": (
                                f"Optional model to use. Available options: {models_str}. "
                                f"Defaults to system default ({self.default_model})."
                            )
                        }
                    },
                    "required": ["name", "role", "instructions"]
                }
            }
        }

        def create_agent_wrapper(name: str, role: str, instructions: str, model: Optional[str] = None):
            return self.create_agent(name, role, instructions, model, created_by=agent.name)

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
                            "name": {
                                "type": "string",
                                "description": "The name of the team (e.g., 'Frontend', 'Research')."
                            },
                            "goal": {"type": "string", "description": "The primary goal of the team."},
                            "lead_role": {
                                "type": "string",
                                "description": "The role of the team leader (e.g., 'Tech Lead', 'Project Manager')."
                            },
                            "lead_instructions": {
                                "type": "string",
                                "description": "Specific instructions for the team leader on how to manage the team."
                            }
                        },
                        "required": ["name", "goal", "lead_role", "lead_instructions"]
                    }
                }
            }

            def create_team_wrapper(name: str, goal: str, lead_role: str, lead_instructions: str):
                return self.create_team(name, goal, lead_role, lead_instructions)

            agent.register_tool(create_team_wrapper, create_team_schema)

            # Tool: Remove Agent (Main Agent Only)
            remove_agent_schema = {
                "type": "function",
                "function": {
                    "name": "remove_agent",
                    "description": "Removes/dismisses a sub-agent from the swarm.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "The name of the agent to remove."}
                        },
                        "required": ["name"]
                    }
                }
            }

            def remove_agent_wrapper(name: str):
                try:
                    self.remove_agent(name)
                    return f"Agent '{name}' removed."
                except Exception as e:
                    return f"Error: {str(e)}"

            agent.register_tool(remove_agent_wrapper, remove_agent_schema)

            # Tool: Toggle Agent (Main Agent Only)
            toggle_agent_schema = {
                "type": "function",
                "function": {
                    "name": "toggle_agent",
                    "description": "Activates or deactivates an agent.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "The name of the agent."}
                        },
                        "required": ["name"]
                    }
                }
            }

            def toggle_agent_wrapper(name: str):
                try:
                    return self.toggle_agent(name)
                except Exception as e:
                    return f"Error: {str(e)}"

            agent.register_tool(toggle_agent_wrapper, toggle_agent_schema)

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
            with self._lock:
                target_agent = self.agents.get(to_agent)
                agent_names = list(self.agents.keys())

            if not target_agent:
                return f"Error: Agent '{to_agent}' not found. Available agents: {agent_names}"

            # Record interaction
            summary = task[:50] + "..." if len(task) > 50 else task
            timestamp = datetime.datetime.now().isoformat()

            with self._lock:
                self.interactions.append({
                    "source": agent.name,
                    "target": to_agent,
                    "summary": summary,  # Brief summary
                    "timestamp": timestamp
                })

                # Keep only last 20 interactions
                if len(self.interactions) > 20:
                    self.interactions.pop(0)

            # Activity Log - outside lock, request scoped
            self._log_activity({
                "type": "interaction",
                "source": agent.name,
                "target": to_agent,
                "summary": summary,
                "timestamp": timestamp
            })

            # We add the sender's context implicitly by just chatting with the target
            # In a more complex system, we'd pass the sender's name.
            try:
                response = target_agent.chat(f"Request from {agent.name}: {task}")
            except Exception as e:
                response = f"Error: Delegation to '{to_agent}' failed: {str(e)}"

            response_summary = "Response: " + (response[:50] + "..." if len(response) > 50 else response)
            response_timestamp = datetime.datetime.now().isoformat()

            with self._lock:
                # Record response interaction
                self.interactions.append({
                    "source": to_agent,
                    "target": agent.name,
                    "summary": response_summary,
                    "timestamp": response_timestamp
                })

                if len(self.interactions) > 20:
                    self.interactions.pop(0)

            # Activity Log - outside lock, request scoped
            self._log_activity({
                "type": "interaction",
                "source": to_agent,
                "target": agent.name,
                "summary": response_summary,
                "timestamp": response_timestamp
            })

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
            with self._lock:
                agent_list = list(self.agents.keys())
                team_list = list(self.teams.keys())
            return f"Available agents: {agent_list}. Teams: {team_list}"

        agent.register_tool(list_agents_wrapper, list_agents_schema)

    def update_settings(self):
        """Reloads configuration and updates agents."""
        # Allow env var to override default model
        self.default_model = settings.llm_model or "gpt-4o"

        with self._lock:
            # Update existing agents to use the new default model if they aren't custom
            for agent in self.agents.values():
                if not getattr(agent, "is_custom_model", False):
                    agent.model = self.default_model

                # Re-register tools to update dynamic descriptions (like available models)
                self._register_swarm_tools(agent)

                # Clear client to ensure new auth is picked up if needed
                agent.client = None

    def chat(self, message: str, attachments: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Entry point for the user to chat with the main agent.
        """
        with self._lock:
            main_agent = self.agents[self.main_agent_name]

        # Don't hold lock during LLM inference
        return main_agent.chat(message, attachments=attachments)

    def get_graph_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Returns the current swarm topology and interaction history.
        """
        nodes = []
        with self._lock:
            for name, agent in self.agents.items():
                nodes.append({
                    "id": name,
                    "name": name,
                    "parent": agent.created_by,
                    "status": getattr(agent, "status", "active"),
                    "last_thought": getattr(agent, "last_thought", "Idle")
                })

            # Format edges from interactions
            # We could also add structural edges (parent-child) implicitly in frontend
            # or explicitly here. Let's send interaction edges.
            edges = []
            for interaction in self.interactions:
                edges.append({
                    "source": interaction["source"],
                    "target": interaction["target"],
                    "label": interaction["summary"],
                    "timestamp": interaction.get("timestamp", "")
                })

        return {"nodes": nodes, "edges": edges}
