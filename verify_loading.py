from playwright.sync_api import sync_playwright, expect
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Mock Tauri Internals
    mock_script = """
    window.__TAURI_INTERNALS__ = {
        invoke: async (cmd, args) => {
            console.log(`[Mock] Invoke: ${cmd}`, args);
            if (cmd === 'trigger_capture') {
                // Hang the promise to simulate loading
                await new Promise(r => setTimeout(r, 2000));
                return {};
            }
            return {};
        },
        metadata: { currentWindow: { label: 'main' } },
        plugins: { invoke: async () => {} }
    };
    window.__TAURI_IPC__ = async () => {};
    """

    page.add_init_script(mock_script)

    page.goto("http://localhost:1420")
    page.wait_for_timeout(1000)

    # Locate the capture button specifically inside search bar
    capture_btn = page.locator('.search-bar .icon-button').last

    # Verify initial state
    print("Verifying initial state...")
    expect(capture_btn).not_to_be_disabled()
    expect(capture_btn).to_have_attribute("title", "Capture screenshot")

    print("Clicking button...")
    capture_btn.click()

    # Verify loading state
    print("Verifying loading state...")

    # 1. Spinner should be present inside the button
    spinner = capture_btn.locator('.spinner')
    expect(spinner).to_be_visible()
    print("✅ Spinner is visible")

    # 2. Button should be disabled
    expect(capture_btn).to_be_disabled()
    print("✅ Button is disabled")

    # 3. Title/Aria-label should be updated
    expect(capture_btn).to_have_attribute("aria-label", "Capturing screenshot...")
    expect(capture_btn).to_have_attribute("title", "Capturing screenshot...")
    print("✅ Title/Aria-label updated")

    # Take verification screenshot
    page.screenshot(path="/home/jules/verification/verification.png")
    print("Screenshot saved to /home/jules/verification/verification.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
