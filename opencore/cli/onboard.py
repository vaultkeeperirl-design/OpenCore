import os
from opencore.llm.factory import get_llm_provider


def verify_connection(config):
    """
    Verifies the LLM connection using the provided configuration.
    Returns (True, message) if successful, (False, error_message) otherwise.
    """
    print(">> VERIFYING CONNECTION TO NEURAL BACKBONE...")

    # Store original env to restore later
    original_env = os.environ.copy()

    try:
        # Apply config to os.environ for the factory to use
        for k, v in config.items():
            if v:
                os.environ[k] = str(v)

        # Get model and provider
        model = config.get("LLM_MODEL")
        if not model:
            return False, "No LLM Model configured."

        # Instantiate provider
        # This might raise ValueError if keys are missing
        provider = get_llm_provider(model)

        # Attempt a simple chat completion
        # We use a simple "Hello" message
        response = provider.chat(
            [{"role": "user", "content": "Hello. Just say hi."}]
        )

        if response and response.content:
            return True, "Connection Verified Successfully."
        else:
            return False, "Provider returned empty response."

    except Exception as e:
        return False, str(e)
    finally:
        # Restore environment variables to avoid polluting the process
        os.environ.clear()
        os.environ.update(original_env)


def run_onboarding(interactive=True):
    config = {}

    if not interactive:
        print("\n--- OPENCORE // AUTO-SETUP ---")
        print(">> INITIALIZING DEFAULT CONFIGURATION MATRIX...")
        config = {
            "APP_ENV": "production",
            "HOST": "127.0.0.1",
            "PORT": "8000",
            "LLM_MODEL": "gpt-4o",
            "HEARTBEAT_INTERVAL": "3600",
            "OPENAI_API_KEY": ""
        }
    else:
        print("\n--- OPENCORE // SYSTEM INITIALIZATION ---")
        print(
            "SYSTEM ONLINE. NEURAL INTERFACE ACTIVE. "
            "CONFIGURING ENVIRONMENT MATRIX."
        )

        # Default settings (can be changed in .env later)
        config["APP_ENV"] = "production"
        config["HOST"] = "127.0.0.1"
        config["PORT"] = "8000"
        config["HEARTBEAT_INTERVAL"] = "3600"

        while True:
            # LLM Provider Selection
            print("\nSELECT NEURAL BACKBONE ::")
            print("1. OpenAI (GPT-4o, GPT-3.5)")
            print("2. Anthropic (Claude 3.5 Sonnet, Opus)")
            print("3. Ollama (Local - Llama 3, Qwen, DeepSeek)")
            print("4. Google Gemini (AI Studio - API Key)")
            print("5. Google Vertex AI (Cloud - Project ID)")
            print("6. Grok (xAI)")
            print("7. Mistral AI")
            print("8. Other (Custom)")

            choice = input("INPUT DIRECTIVE (1-8) [DEFAULT: 1]: ").strip()
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
                print(
                    "ENSURE OLLAMA KERNEL IS ACTIVE "
                    "(DEFAULT: http://localhost:11434)."
                )
                model = input(
                    "MODEL IDENTIFIER (e.g., ollama/llama3) "
                    "[DEFAULT: ollama/llama3]: "
                ).strip()
                config["LLM_MODEL"] = model if model else "ollama/llama3"
                base_url = input(
                    "OLLAMA BASE URL [DEFAULT: http://localhost:11434]: "
                ).strip()
                if base_url:
                    config["OLLAMA_API_BASE"] = base_url

            elif choice == "4":
                # Google Gemini (AI Studio)
                config["LLM_MODEL"] = "gemini/gemini-2.0-flash"
                api_key = input("ENTER GEMINI_API_KEY (AI Studio): ").strip()
                config["GEMINI_API_KEY"] = api_key

            elif choice == "5":
                # Vertex AI
                config["LLM_MODEL"] = "vertex_ai/gemini-1.5-pro"
                project_id = input("GOOGLE CLOUD PROJECT ID: ").strip()
                location = input("REGION (e.g., us-central1): ").strip()
                config["VERTEX_PROJECT"] = project_id
                config["VERTEX_LOCATION"] = location
                print(
                    "NOTE: AUTHENTICATE VIA "
                    "`gcloud auth application-default login`."
                )

            elif choice == "6":
                # Grok
                config["LLM_MODEL"] = "xai/grok-2-vision-1212"
                api_key = input("ENTER XAI_API_KEY (GROK): ").strip()
                config["XAI_API_KEY"] = api_key

            elif choice == "7":
                # Mistral
                config["LLM_MODEL"] = "mistral/mistral-large-latest"
                api_key = input("ENTER MISTRAL_API_KEY: ").strip()
                config["MISTRAL_API_KEY"] = api_key

            else:
                # Custom
                model = input(
                    "ENTER FULL MODEL STRING (provider/model-name): "
                ).strip()
                config["LLM_MODEL"] = model
                print("NOTE: MANUALLY ADD REQUIRED KEYS TO .env FILE.")

            # Verification Step
            success, message = verify_connection(config)

            if success:
                print(f"[{message}]")
                break
            else:
                print(f"\n[CONNECTION FAILED]: {message}")
                retry = input(
                    "RETRY CONFIGURATION? (y/n) [DEFAULT: y]: "
                ).strip().lower()
                if retry == 'n':
                    print(
                        "WARNING: SAVING CONFIGURATION WITHOUT VERIFICATION."
                    )
                    break
                # Loop continues if retry is y or empty

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
