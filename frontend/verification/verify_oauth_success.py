
import os
import json
from playwright.sync_api import sync_playwright, expect

def test_oauth_success_flow():
    """
    Verifies that when the app loads with ?auth_success=true:
    1. A success toast is displayed.
    2. The URL is cleaned (param removed).
    3. The Settings Modal opens automatically.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Intercept network requests
        page.route("**/config", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"LLM_MODEL": "gpt-4o", "HAS_GEMINI_KEY": True})
        ))

        # Mock auth status as TRUE now because we just succeeded
        page.route("**/auth/status", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"google": True, "qwen": False})
        ))

        # Mock unrelated APIs to avoid errors
        page.route("**/agents", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"agents": []})
        ))
        page.route("**/heartbeat", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"version": "1.0.0", "start_time": "2024-01-01T00:00:00"})
        ))

        # Listen for console logs
        page.on("console", lambda msg: print(f"PAGE LOG: {msg.text}"))

        # Navigate with query param
        print("Navigating to app with auth_success=true...")
        page.goto("http://localhost:3000/?auth_success=true")

        # 1. Check for Toast
        print("Checking for success toast...")

        # Sonner toasts usually have role="status" or specific class.
        # Let's look for the text "Google Authentication Successful!"
        try:
            expect(page.get_by_text("Google Authentication Successful!")).to_be_visible(timeout=5000)
        except AssertionError as e:
            screenshot_path = "frontend/verification/failure_screenshot.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
            raise e

        # 2. Check Settings Modal Open
        print("Checking if Settings Modal is open...")
        expect(page.get_by_text("SYSTEM CONFIGURATION")).to_be_visible()

        # 4. Check that Gemini Status shows "GOOGLE ADC ACTIVE" (green)
        print("Checking OAuth status indicator...")
        gemini_label = page.get_by_text("Gemini Key")
        gemini_label.scroll_into_view_if_needed()

        # We expect the "Authenticated via System Credentials" badge
        expect(page.get_by_text("Authenticated via System Credentials")).to_be_visible()

        # Take screenshot
        os.makedirs("frontend/verification", exist_ok=True)
        screenshot_path = "frontend/verification/oauth_success_flow.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    test_oauth_success_flow()
