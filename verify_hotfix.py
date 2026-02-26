from playwright.sync_api import sync_playwright, expect
import os

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # Go to the app
    page.goto("http://localhost:8000")

    # Wait for the page to load
    page.wait_for_load_state("networkidle")

    # Take a screenshot of the initial state
    if not os.path.exists("verification"):
        os.makedirs("verification")
    page.screenshot(path="verification/initial_load.png")
    print("Initial screenshot taken.")

    # Locate the drop zone (the main container)
    # The container has "bg-bg-secondary/50" class
    # We can also try to find it by text or other attributes if classes are hashed (but here they seem to be Tailwind utility classes)

    # Let's try to inject a script to simulate the drop
    # We create a large file (11MB)

    js_drop_script = """
        const dataTransfer = new DataTransfer();
        const file = new File(['a'.repeat(11 * 1024 * 1024)], 'large_file.txt', { type: 'text/plain' });
        dataTransfer.items.add(file);

        const event = new DragEvent('drop', {
            bubbles: true,
            cancelable: true,
            dataTransfer: dataTransfer
        });

        // Find the drop zone. It's the main container.
        // We can target the element that contains "System Online" text if we are not sure about classes
        const dropZone = document.querySelector('div.flex.flex-col.h-full');
        if (dropZone) {
            dropZone.dispatchEvent(event);
            console.log("Drop event dispatched");
        } else {
            console.error("Drop zone not found");
        }
    """

    page.evaluate(js_drop_script)

    # Wait for the toast to appear
    # The toast contains "File too large"
    try:
        # Sonner toasts usually appear in a list
        # We look for the text
        toast = page.get_by_text("File too large")
        toast.wait_for(state="visible", timeout=5000)
        print("Toast found!")

        # Take a screenshot of the toast
        page.screenshot(path="verification/toast_visible.png")
        print("Toast screenshot taken.")

    except Exception as e:
        print(f"Error finding toast: {e}")
        page.screenshot(path="verification/toast_failed.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
