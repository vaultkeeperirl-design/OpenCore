# OpenCore

OpenCore is a powerful Python-based AI Agent Swarm system, inspired by OpenClaw but designed for dynamic agent collaboration. It allows you to run a team of autonomous agents that can communicate, delegate tasks, and execute tools on your local machine.

## Features

- **Agent Swarms**: A main "Manager" agent can spawn new sub-agents (e.g., "Coder", "Researcher") on the fly.
- **Hierarchical Delegation**: Agents can delegate tasks to other agents and wait for results.
- **Tool Use**: Agents have built-in access to file system operations and command execution.
- **Multi-Provider Support**: Supports OpenAI, Google Vertex AI, AWS Bedrock, Anthropic, Mistral, Groq, and Ollama (Local) via `litellm`.
- **Chat Interface**: A clean, web-based chat interface to interact with your swarm.
- **Accessibility**: Screen reader support and keyboard navigation for a better user experience.
- **Extensible**: Easy to add new tools or agent types.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/vaultkeeperirl-design/OpenCore.git
    cd opencore
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables**:
    Create a `.env` file in the root directory.

## Configuration

You can configure the application using environment variables in your `.env` file.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `APP_ENV` | Application environment (`development` or `production`). | `production` |
| `LLM_MODEL` | The LLM model to use (see Supported Models below). | `gpt-4o` |
| `HOST` | The host to bind the server to. | `0.0.0.0` |
| `PORT` | The port to listen on. | `8000` |
| `LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). | `INFO` |

## Supported Models & Providers

You can control which model the swarm uses by setting the `LLM_MODEL` environment variable in your `.env` file. You also need to provide the relevant API keys or authentication.

### 1. OpenAI (Default)
Standard usage with GPT models.
```bash
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-...
```

### 2. Ollama (Local) - Recommended for Qwen, DeepSeek, Llama 3
Run open-weights models locally without API keys.
1.  Install [Ollama](https://ollama.com).
2.  Pull the model you want (e.g., `ollama pull qwen2.5` or `ollama pull deepseek-coder`).
3.  Configure `.env`:
    ```bash
    # Qwen
    LLM_MODEL=ollama/qwen2.5

    # DeepSeek
    LLM_MODEL=ollama/deepseek-coder

    # Llama 3
    LLM_MODEL=ollama/llama3
    ```

### 3. Anthropic
Use Claude 3.5 Sonnet or Opus.
```bash
LLM_MODEL=anthropic/claude-3-5-sonnet-20240620
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Google Vertex AI (Gemini)
Use Google's Gemini models via Vertex AI (keyless auth via `gcloud`).
1.  Authenticate: `gcloud auth application-default login`
2.  Configure `.env`:
    ```bash
    LLM_MODEL=vertex_ai/gemini-1.5-pro
    VERTEX_PROJECT=your-project-id
    VERTEX_LOCATION=us-central1
    ```

### 5. AWS Bedrock
Use models hosted on AWS Bedrock (Claude, Titan, Mistral, Llama).
1.  Authenticate: `aws configure` or `aws sso login`.
2.  Configure `.env`:
    ```bash
    # Claude on Bedrock
    LLM_MODEL=bedrock/anthropic.claude-3-sonnet-20240229-v1:0

    # Llama 3 on Bedrock
    LLM_MODEL=bedrock/meta.llama3-70b-instruct-v1:0
    ```

### 6. Mistral AI
Use Mistral's API directly.
```bash
LLM_MODEL=mistral/mistral-large-latest
MISTRAL_API_KEY=...
```

### 7. Groq
Use Groq for ultra-fast inference (Llama 3, Mixtral).
```bash
LLM_MODEL=groq/llama3-70b-8192
GROQ_API_KEY=gsk_...
```

### 8. DeepSeek (API)
If using the DeepSeek API directly instead of Ollama.
```bash
LLM_MODEL=deepseek/deepseek-coder
DEEPSEEK_API_KEY=sk-...
```

## Usage

1.  **Start the Server**:
    ```bash
    python3 main.py
    ```
    This will start the backend server. By default, it runs on `http://0.0.0.0:8000`.
    Check the console output for logs (controlled by `LOG_LEVEL`).

2.  **Access the Interface**:
    Open your browser and navigate to `http://localhost:8000` (or the port you configured).

3.  **Chat with the Swarm**:
    - Type a message to the Manager.
    - Example: "Create a 'PythonCoder' agent using `ollama/qwen2.5` and ask it to write a snake game."
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
