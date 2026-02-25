from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        print("Navigating to http://localhost:3000...")
        page.goto("http://localhost:3000")

        # Wait for the chat interface to load (look for the input field or send button)
        page.wait_for_selector('input[aria-label="Chat input"]', timeout=30000)

        print("Page loaded. Checking for VoiceInput button...")

        # Locate the button by its new aria-label
        voice_button = page.locator('button[aria-label="Start voice input"]')

        if voice_button.count() > 0:
            print("VoiceInput button found by aria-label!")

            # Check aria-pressed
            aria_pressed = voice_button.get_attribute("aria-pressed")
            print(f"aria-pressed: {aria_pressed}")

            if aria_pressed == "false":
                print("aria-pressed is correctly set to false.")
            else:
                print(f"ERROR: aria-pressed is {aria_pressed}, expected 'false'")

            # Take a screenshot of the button area
            voice_button.screenshot(path="voice_input_button.png")
            page.screenshot(path="full_page.png")
            print("Screenshots saved.")

        else:
            print("ERROR: VoiceInput button NOT found by aria-label.")
            # Take a screenshot for debugging
            page.screenshot(path="debug_page.png")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="error_page.png")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
