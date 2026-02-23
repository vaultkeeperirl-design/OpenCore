def run_onboarding(interactive=True):
    config = {}

    if not interactive:
        print("\n--- OpenCore Auto-Setup ---")
        print("Creating default configuration...")
        config = {
            "APP_ENV": "production",
            "HOST": "0.0.0.0",
            "PORT": "8000",
            "LLM_MODEL": "gpt-4o",
            "HEARTBEAT_INTERVAL": "3600",
            "OPENAI_API_KEY": ""
        }
    else:
        print("\n--- OpenCore Onboarding ---")
        print("Welcome! Let's get your AI Swarm environment set up.")

        # 1. Environment
        app_env = input("Environment (development/production) [default: production]: ").strip()
        config["APP_ENV"] = app_env if app_env else "production"

        # 2. Host and Port
        host = input("Host [default: 0.0.0.0]: ").strip()
        config["HOST"] = host if host else "0.0.0.0"

        port = input("Port [default: 8000]: ").strip()
        config["PORT"] = port if port else "8000"

        # 3. LLM Provider Selection
        print("\nSelect your LLM Provider:")
        print("1. OpenAI (GPT-4o, GPT-3.5)")
        print("2. Anthropic (Claude 3.5 Sonnet, Opus)")
        print("3. Ollama (Local - Llama 3, Qwen, DeepSeek)")
        print("4. Google Vertex AI (Gemini)")
        print("5. Grok (xAI)")
        print("6. Mistral AI")
        print("7. Other (Custom)")

        choice = input("Enter choice (1-7) [default: 1]: ").strip()
        if not choice:
            choice = "1"

        if choice == "1":
            # OpenAI
            model = input("Model name [default: gpt-4o]: ").strip()
            config["LLM_MODEL"] = model if model else "gpt-4o"
            api_key = input("Enter your OPENAI_API_KEY: ").strip()
            config["OPENAI_API_KEY"] = api_key

        elif choice == "2":
            # Anthropic
            model = input("Model name [default: anthropic/claude-3-5-sonnet-20240620]: ").strip()
            config["LLM_MODEL"] = model if model else "anthropic/claude-3-5-sonnet-20240620"
            api_key = input("Enter your ANTHROPIC_API_KEY: ").strip()
            config["ANTHROPIC_API_KEY"] = api_key

        elif choice == "3":
            # Ollama
            print("Ensure Ollama is running (typically http://localhost:11434).")
            model = input("Model name (e.g., ollama/llama3) [default: ollama/llama3]: ").strip()
            config["LLM_MODEL"] = model if model else "ollama/llama3"
            base_url = input("Ollama Base URL [default: http://localhost:11434]: ").strip()
            if base_url:
                config["OLLAMA_API_BASE"] = base_url

        elif choice == "4":
            # Vertex AI
            model = input("Model name [default: vertex_ai/gemini-1.5-pro]: ").strip()
            config["LLM_MODEL"] = model if model else "vertex_ai/gemini-1.5-pro"
            project_id = input("Google Cloud Project ID: ").strip()
            location = input("Region (e.g., us-central1): ").strip()
            config["VERTEX_PROJECT"] = project_id
            config["VERTEX_LOCATION"] = location
            print("Note: Ensure you have authenticated with `gcloud auth application-default login`.")

        elif choice == "5":
            # Grok
            model = input("Model name [default: openai/grok-2-1212]: ").strip()
            config["LLM_MODEL"] = model if model else "openai/grok-2-1212"
            api_key = input("Enter your XAI_API_KEY (Grok): ").strip()
            config["OPENAI_API_KEY"] = api_key # Grok uses OpenAI compatibility
            config["OPENAI_API_BASE"] = "https://api.x.ai/v1"

        elif choice == "6":
            # Mistral
            model = input("Model name [default: mistral/mistral-large-latest]: ").strip()
            config["LLM_MODEL"] = model if model else "mistral/mistral-large-latest"
            api_key = input("Enter your MISTRAL_API_KEY: ").strip()
            config["MISTRAL_API_KEY"] = api_key

        else:
            # Custom
            model = input("Enter full model string (e.g., provider/model-name): ").strip()
            config["LLM_MODEL"] = model
            print("You may need to manually add specific API keys to the .env file later.")

        # 4. Heartbeat
        interval = input("\nHeartbeat Interval (seconds) [default: 3600]: ").strip()
        config["HEARTBEAT_INTERVAL"] = interval if interval else "3600"

    # Write to .env
    print("\nWriting configuration to .env file...")
    with open(".env", "w") as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")

    print("Configuration saved successfully!")
    if not interactive:
        print("Please configure your API keys in the application settings.")
    else:
        print("You can edit the .env file manually anytime.")
    print("Starting OpenCore...\n")
