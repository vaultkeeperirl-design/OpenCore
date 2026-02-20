# OpenCore

OpenCore is a powerful Python-based AI Agent Swarm system, inspired by OpenClaw but designed for dynamic agent collaboration. It allows you to run a team of autonomous agents that can communicate, delegate tasks, and execute tools on your local machine.

## Features

- **Agent Swarms**: A main "Manager" agent can spawn new sub-agents (e.g., "Coder", "Researcher") on the fly.
- **Hierarchical Delegation**: Agents can delegate tasks to other agents and wait for results.
- **Tool Use**: Agents have built-in access to file system operations and command execution.
- **Chat Interface**: A clean, web-based chat interface to interact with your swarm.
- **Extensible**: easy to add new tools or agent types.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/opencore.git
    cd opencore
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You can create a requirements.txt with `pip freeze > requirements.txt`)*

3.  **Set up Environment Variables**:
    Create a `.env` file in the root directory and add your OpenAI API Key:
    ```
    OPENAI_API_KEY=sk-your-api-key-here
    ```
    OpenCore uses the OpenAI API (or compatible endpoints) for agent intelligence.

## Usage

1.  **Start the Server**:
    ```bash
    python3 main.py
    ```
    This will start the backend server on `http://localhost:8000`.

2.  **Access the Interface**:
    Open your browser and navigate to `http://localhost:8000`.

3.  **Chat with the Swarm**:
    - Type a message to the Manager.
    - Example: "Create a 'PythonCoder' agent and ask it to write a hello world script in `hello.py`."
    - The Manager will spawn the agent, delegate the task, and report back.

## Project Structure

-   `opencore/core/`: Core logic for `Agent` and `Swarm`.
-   `opencore/tools/`: Standard tools (Filesystem, System).
-   `opencore/interface/`: FastAPI backend and HTML frontend.
-   `main.py`: Application entry point.

## Testing

Run the test suite to verify functionality:
```bash
python3 -m unittest discover tests
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
