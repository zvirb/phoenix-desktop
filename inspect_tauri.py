from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Go to app
    page.goto("http://localhost:1420")

    # Wait for hydration
    page.wait_for_timeout(2000)

    # Inspect window properties related to Tauri
    properties = page.evaluate("""() => {
        const keys = [];
        for (const key in window) {
            if (key.includes("TAURI")) {
                keys.push(key);
            }
        }
        return keys;
    }""")

    print("Window properties:", properties)

    # Also try to see if we can access the internals
    internals = page.evaluate("""() => {
        return window.__TAURI_INTERNALS__ ? Object.keys(window.__TAURI_INTERNALS__) : "Not Found";
    }""")
    print("Internals:", internals)

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
