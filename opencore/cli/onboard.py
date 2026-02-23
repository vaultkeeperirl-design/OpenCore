def run_onboarding(interactive=True):
    config = {}

    if not interactive:
        print("\n--- OPENCORE // AUTO-SETUP ---")
        print(">> INITIALIZING DEFAULT CONFIGURATION MATRIX...")
        config = {
            "APP_ENV": "production",
            "HOST": "0.0.0.0",
            "PORT": "8000",
            "LLM_MODEL": "gpt-4o",
            "HEARTBEAT_INTERVAL": "3600",
            "OPENAI_API_KEY": ""
        }
    else:
        print("\n--- OPENCORE // SYSTEM INITIALIZATION ---")
        print("SYSTEM ONLINE. NEURAL INTERFACE ACTIVE. CONFIGURING ENVIRONMENT MATRIX.")

        # Default settings (can be changed in .env later)
        config["APP_ENV"] = "production"
        config["HOST"] = "0.0.0.0"
        config["PORT"] = "8000"
        config["HEARTBEAT_INTERVAL"] = "3600"

        # LLM Provider Selection
        print("\nSELECT NEURAL BACKBONE ::")
        print("1. OpenAI (GPT-4o, GPT-3.5)")
        print("2. Anthropic (Claude 3.5 Sonnet, Opus)")
        print("3. Ollama (Local - Llama 3, Qwen, DeepSeek)")
        print("4. Google Vertex AI (Gemini)")
        print("5. Grok (xAI)")
        print("6. Mistral AI")
        print("7. Other (Custom)")

        choice = input("INPUT DIRECTIVE (1-7) [DEFAULT: 1]: ").strip()
        if not choice:
            choice = "1"

        if choice == "1":
            # OpenAI
            config["LLM_MODEL"] = "gpt-4o"
            api_key = input("ENTER OPENAI_API_KEY: ").strip()
            config["OPENAI_API_KEY"] = api_key

        elif choice == "2":
            # Anthropic
            config["LLM_MODEL"] = "anthropic/claude-3-5-sonnet-20240620"
            api_key = input("ENTER ANTHROPIC_API_KEY: ").strip()
            config["ANTHROPIC_API_KEY"] = api_key

        elif choice == "3":
            # Ollama
            print("ENSURE OLLAMA KERNEL IS ACTIVE (DEFAULT: http://localhost:11434).")
            model = input("MODEL IDENTIFIER (e.g., ollama/llama3) [DEFAULT: ollama/llama3]: ").strip()
            config["LLM_MODEL"] = model if model else "ollama/llama3"
            base_url = input("OLLAMA BASE URL [DEFAULT: http://localhost:11434]: ").strip()
            if base_url:
                config["OLLAMA_API_BASE"] = base_url

        elif choice == "4":
            # Vertex AI
            config["LLM_MODEL"] = "vertex_ai/gemini-1.5-pro"
            project_id = input("GOOGLE CLOUD PROJECT ID: ").strip()
            location = input("REGION (e.g., us-central1): ").strip()
            config["VERTEX_PROJECT"] = project_id
            config["VERTEX_LOCATION"] = location
            print("NOTE: AUTHENTICATE VIA `gcloud auth application-default login`.")

        elif choice == "5":
            # Grok
            config["LLM_MODEL"] = "xai/grok-2-vision-1212"
            api_key = input("ENTER XAI_API_KEY (GROK): ").strip()
            config["XAI_API_KEY"] = api_key

        elif choice == "6":
            # Mistral
            config["LLM_MODEL"] = "mistral/mistral-large-latest"
            api_key = input("ENTER MISTRAL_API_KEY: ").strip()
            config["MISTRAL_API_KEY"] = api_key

        else:
            # Custom
            model = input("ENTER FULL MODEL STRING (provider/model-name): ").strip()
            config["LLM_MODEL"] = model
            print("NOTE: MANUALLY ADD REQUIRED KEYS TO .env FILE.")

    # Write to .env
    print("\nWRITING CONFIGURATION TO .env FILE...")
    with open(".env", "w") as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")

    print(">> CONFIGURATION MATRIX UPDATED.")
    if not interactive:
        print("PLEASE CONFIGURE API KEYS IN SYSTEM SETTINGS.")
    else:
        print("NOTE: .env FILE ACCESSIBLE FOR MANUAL OVERRIDE.")
    print("STARTING OPENCORE SYSTEM...\n")
