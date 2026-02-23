import time
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # Mock Tauri invoke
    page.add_init_script("""
        window.__TAURI_INTERNALS__ = {
            invoke: async (cmd, args, options) => {
                console.log(`[Mock] invoke called: ${cmd}`, args);
                if (cmd === 'decompose_task') {
                    // Simulate delay to capture the "Thinking..." state
                    await new Promise(resolve => setTimeout(resolve, 3000));
                    return { success: true, data: { subtasks: ["Task 1", "Task 2"] } };
                }
                return {};
            },
            metadata: {}
        };
        // Mock window.__TAURI_IPC__ just in case
        window.__TAURI_IPC__ = async () => {};
    """)

    page.goto("http://localhost:3000")

    # Wait for app to load
    page.wait_for_selector(".search-bar")

    # 1. Verify Clear Button Title
    print("Verifying Clear Button Title...")
    page.fill("input[aria-label='Task description']", "Test Task")
    # Clear button should appear
    clear_btn = page.locator("button[aria-label='Clear task']")
    clear_btn.wait_for(state="visible")

    # Check title attribute
    title = clear_btn.get_attribute("title")
    print(f"Clear Button Title: {title}")
    assert title == "Clear task", f"Expected 'Clear task', got '{title}'"

    # 2. Verify Pulse Animation (Busy State)
    print("Verifying Pulse Animation...")
    # Click Submit
    submit_btn = page.locator("button[title='Submit task']") # Using title to locate since we just verified standard buttons use titles
    submit_btn.click()

    # Wait for busy state
    page.wait_for_selector(".search-bar[aria-busy='true']")

    # Also verify placeholder changed
    placeholder = page.get_attribute("input[aria-label='Task description']", "placeholder")
    print(f"Placeholder during loading: {placeholder}")
    assert placeholder == "Thinking...", f"Expected 'Thinking...', got '{placeholder}'"

    # Take screenshot of busy state
    page.screenshot(path="verification_busy.png")
    print("Screenshot taken: verification_busy.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
