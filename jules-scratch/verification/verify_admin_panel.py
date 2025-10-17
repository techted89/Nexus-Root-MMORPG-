from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()

    # Start the server in the background before running this script
    page.goto("http://localhost:8080/admin")

    # Log in
    page.fill("#username", "admin")
    page.fill("#password", "password")
    page.click("button[type=submit]")

    # Wait for the players table to be visible
    page.wait_for_selector("#players-table")

    # Take a screenshot
    page.screenshot(path="jules-scratch/verification/verification.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)