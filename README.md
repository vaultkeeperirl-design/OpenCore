# OpenCore // SYSTEM.ACTIVE

**OpenCore** is a **neural operating system for autonomous agent swarms**.
Designed for dynamic collaboration, it orchestrates a network of specialized intelligence nodes to execute complex directives on your local infrastructure.

> *Inspired by OpenClaw, engineered for the next generation of agentic workflows.*

## // CORE_MODULES

-   **Swarm Intelligence**: A central "Manager" node spawns and orchestrates sub-agents ("Coder", "Researcher") in real-time.
-   **Neural Link**: Agents communicate, delegate, and synthesize information hierarchically.
-   **Hardline Access**: Direct file system manipulation and command execution capabilities.
-   **Multi-Model Matrix**: Seamless integration with OpenAI, Vertex AI, Bedrock, Anthropic, Mistral, Groq, and local Ollama nodes via `litellm`.
-   **Cyberdeck Interface**: A reactive, cyberpunk-themed command center for swarm interaction.
-   **Accessibility Protocol**: Full screen reader support and keyboard navigation.

## // DEPLOYMENT_PROTOCOL

1.  **Clone Repository**:
    ```bash
    git clone https://github.com/vaultkeeperirl-design/OpenCore.git
    cd opencore
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -e .
    ```

3.  **Initialize System**:
    Run the onboarding wizard to configure your environment matrix:
    ```bash
    opencore onboard
    ```

## // CONFIGURATION_MATRIX

Configure the application using environment variables in your `.env` file.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `APP_ENV` | Application environment (`development` or `production`). | `production` |
| `LLM_MODEL` | The LLM model to use (see Supported Models below). | `gpt-4o` |
| `HOST` | The host to bind the server to. | `0.0.0.0` |
| `PORT` | The port to listen on. | `8000` |
| `LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). | `INFO` |

## // NEURAL_LINK_INTEGRATIONS (Supported Models)

Control which model the swarm uses by setting the `LLM_MODEL` environment variable. Ensure relevant API keys or authentication are active.

### 1. OpenAI (Default)
Standard usage with GPT models.
```bash
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-...
```

### 2. Ollama (Local) - Recommended for Qwen, DeepSeek, Llama 3
Run open-weights models locally without API keys.
1.  Install [Ollama](https://ollama.com).
2.  Pull the model (e.g., `ollama pull qwen2.5`).
3.  Configure `.env`:
    ```bash
    LLM_MODEL=ollama/qwen2.5
    ```

### 3. Anthropic
Use Claude 3.5 Sonnet or Opus.
```bash
LLM_MODEL=anthropic/claude-3-5-sonnet-20240620
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Google Vertex AI (Gemini)
Use Google's Gemini models via Vertex AI (keyless auth via `gcloud`).
```bash
LLM_MODEL=vertex_ai/gemini-1.5-pro
VERTEX_PROJECT=your-project-id
VERTEX_LOCATION=us-central1
```

### 5. AWS Bedrock
Use models hosted on AWS Bedrock.
```bash
LLM_MODEL=bedrock/anthropic.claude-3-sonnet-20240229-v1:0
```

### 6. Mistral AI
Use Mistral's API directly.
```bash
LLM_MODEL=mistral/mistral-large-latest
MISTRAL_API_KEY=...
```

### 7. Groq
Use Groq for ultra-fast inference.
```bash
LLM_MODEL=groq/llama3-70b-8192
GROQ_API_KEY=gsk_...
```

## // OPERATIONAL_PROCEDURES

1.  **Start the System**:
    ```bash
    opencore start
    ```
    Alternatively: `python3 main.py`.
    Server binds to `http://0.0.0.0:8000` by default.

2.  **Access the Cyberdeck**:
    Navigate to `http://localhost:8000`.

3.  **Execute Command Sequence**:
    -   Input a directive to the Manager.
    -   Example: "Create a 'PythonCoder' agent using `ollama/qwen2.5` and ask it to write a snake game."
    -   Observe the Manager spawn agents and delegate tasks.

## // SYSTEM_ARCHITECTURE

-   `opencore/core/`: Core logic for `Agent` and `Swarm`.
-   `opencore/tools/`: Standard tools (Filesystem, System).
-   `opencore/interface/`: FastAPI backend and HTML frontend.
-   `main.py`: Application entry point.

## // DIAGNOSTICS

Run the test suite to verify system integrity:
```bash
python3 -m unittest discover tests
```

## // CONTRIBUTING_NODES

Pull requests are welcome. For major architectural changes, please open an issue first to discuss.

## // LICENSE

[AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.en.html)
