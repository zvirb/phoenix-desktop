from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Capture console logs
    page.on("console", lambda msg: print(f"Console: {msg.text}"))

    page.goto("http://localhost:1420")
    page.wait_for_timeout(2000)

    # Click capture button
    # It's the button with "Capture screenshot" title/aria-label
    # Use a locator that finds the button
    button = page.locator('button[title="Capture screenshot"]')
    if button.count() > 0:
        print("Found capture button")
        button.click()
    else:
        print("Capture button not found")

    page.wait_for_timeout(2000)
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
