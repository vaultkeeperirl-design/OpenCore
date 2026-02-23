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

        # Default settings (can be changed in .env later)
        config["APP_ENV"] = "production"
        config["HOST"] = "0.0.0.0"
        config["PORT"] = "8000"
        config["HEARTBEAT_INTERVAL"] = "3600"

        # LLM Provider Selection
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
            config["LLM_MODEL"] = "gpt-4o"
            api_key = input("Enter your OPENAI_API_KEY: ").strip()
            config["OPENAI_API_KEY"] = api_key

        elif choice == "2":
            # Anthropic
            config["LLM_MODEL"] = "anthropic/claude-3-5-sonnet-20240620"
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
            config["LLM_MODEL"] = "vertex_ai/gemini-1.5-pro"
            project_id = input("Google Cloud Project ID: ").strip()
            location = input("Region (e.g., us-central1): ").strip()
            config["VERTEX_PROJECT"] = project_id
            config["VERTEX_LOCATION"] = location
            print("Note: Ensure you have authenticated with `gcloud auth application-default login`.")

        elif choice == "5":
            # Grok
            model = input("Model name [default: xai/grok-2-vision-1212]: ").strip()
            config["LLM_MODEL"] = model if model else "xai/grok-2-vision-1212"
            api_key = input("Enter your XAI_API_KEY (Grok): ").strip()
            config["XAI_API_KEY"] = api_key

        elif choice == "6":
            # Mistral
            config["LLM_MODEL"] = "mistral/mistral-large-latest"
            api_key = input("Enter your MISTRAL_API_KEY: ").strip()
            config["MISTRAL_API_KEY"] = api_key

        else:
            # Custom
            model = input("Enter full model string (e.g., provider/model-name): ").strip()
            config["LLM_MODEL"] = model
            print("You may need to manually add specific API keys to the .env file later.")

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
