# OpenCore

OpenCore is a powerful Python-based AI Agent Swarm system, inspired by OpenClaw but designed for dynamic agent collaboration. It allows you to run a team of autonomous agents that can communicate, delegate tasks, and execute tools on your local machine.

## Features

- **Agent Swarms**: A main "Manager" agent can spawn new sub-agents (e.g., "Coder", "Researcher") on the fly.
- **Hierarchical Delegation**: Agents can delegate tasks to other agents and wait for results.
- **Tool Use**: Agents have built-in access to file system operations and command execution.
- **Multi-Provider Support**: Supports OpenAI, Google Vertex AI, AWS Bedrock, and Ollama (Local) via `litellm`.
- **Chat Interface**: A clean, web-based chat interface to interact with your swarm.
- **Extensible**: Easy to add new tools or agent types.

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

3.  **Set up Environment Variables**:
    Create a `.env` file in the root directory.

    **For OpenAI:**
    ```bash
    OPENAI_API_KEY=sk-your-api-key-here
    ```

    **For Google Vertex AI:**
    Ensure you are authenticated via gcloud CLI:
    ```bash
    gcloud auth application-default login
    ```
    Then configure the project (optional if using default):
    ```bash
    VERTEX_PROJECT=your-project-id
    VERTEX_LOCATION=us-central1
    ```

    **For AWS Bedrock:**
    Ensure you are authenticated via AWS CLI:
    ```bash
    aws configure
    # or
    aws sso login
    ```

    **For Ollama (Local):**
    Ensure Ollama is running (`ollama serve`). No API key required.

## Configuration

You can set the default model for the swarm using the `LLM_MODEL` environment variable.

-   **OpenAI**: `LLM_MODEL=gpt-4o` (default)
-   **Google Vertex AI**: `LLM_MODEL=vertex_ai/gemini-pro`
-   **AWS Bedrock**: `LLM_MODEL=bedrock/anthropic.claude-v2`
-   **Ollama**: `LLM_MODEL=ollama/llama3`

Example `.env`:
```
LLM_MODEL=ollama/llama3
```

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
    - Example: "Create a 'PythonCoder' agent using `ollama/codellama` and ask it to write a hello world script."
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
