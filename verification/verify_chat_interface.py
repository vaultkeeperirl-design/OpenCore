
import asyncio
from playwright.async_api import async_playwright, expect

async def verify_chat_interface():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Wait for the frontend to be ready
        try:
            await page.goto("http://localhost:3000", timeout=60000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            await browser.close()
            return

        # Check for the presence of the attachment button
        # The button has aria-label="Attach files" and contains a Paperclip icon
        attach_button = page.get_by_label("Attach files")
        await expect(attach_button).to_be_visible()

        # Check for the presence of the hidden file input
        file_input = page.locator('input[type="file"]')
        # It's hidden, so we check existence in DOM, not visibility
        count = await file_input.count()
        assert count == 1, "File input not found"

        # Take a screenshot of the chat interface with the button
        await page.screenshot(path="verification/chat_interface_with_attachment.png")
        print("Screenshot saved to verification/chat_interface_with_attachment.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_chat_interface())
