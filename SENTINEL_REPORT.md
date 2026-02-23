Title:
🔮 Sentinel: Proactive insight on Unbounded Conversation History

Description:

👀 Observation:
The `Agent` class in `opencore/core/agent.py` accumulates conversation history in `self.messages` indefinitely. Since the `Manager` agent in the `Swarm` system is long-lived and persists throughout the application lifecycle, its message history grows linearly with every user interaction.

⚠️ Impact:
- **Context Window Exhaustion:** Eventually, the token count will exceed the LLM's context window limit (e.g., 128k for gpt-4o), causing API errors and service disruption.
- **Increased Latency & Cost:** Every request sends the full history to the LLM provider. As history grows, processing time and cost increase linearly.
- **Degraded Reasoning:** Extremely long contexts can sometimes confuse the model or dilute the relevant instructions ("lost in the middle" phenomenon).

🛠️ Suggested Action:
Implement a history management strategy in `Agent.think` or `Agent.add_message`.
- **Sliding Window:** Keep only the last N messages (e.g., last 20 turns) or last M tokens.
- **Summarization:** Periodically summarize older messages into a "memory" block and discard the raw history.
- **Explicit Clearing:** Add a tool or command to clear history when a task is completed.

🔮 Future Benefit:
Ensures the system can run indefinitely without crashing due to memory/context limits, maintains predictable API costs, and keeps agent responses fast and focused.
