from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()

    # Start the server in the background before running this script
    page.goto("http://localhost:8080/")

    # Register a new user
    page.type("#input", "register test_user test_password")
    page.press("#input", "Enter")

    # Wait for the registration message to be visible
    page.wait_for_selector("text=Registration successful.")

    # Log in
    page.type("#input", "login test_user test_password")
    page.press("#input", "Enter")

    # Wait for the login message to be visible
    page.wait_for_selector("text=Login successful. Welcome, test_user.")

    # Register another user
    page.type("#input", "register other_user other_password")
    page.press("#input", "Enter")

    # Wait for the registration message to be visible
    page.wait_for_selector("text=Registration successful.")

    # Test the dos_attack command
    page.type("#input", "dos_attack other_user")
    page.press("#input", "Enter")

    # Wait for the command response to be visible
    page.wait_for_selector("text=DoS attack launched against other_user. Their CPU will be locked for 30 seconds.")

    # Take a screenshot
    page.screenshot(path="jules-scratch/verification/verification.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)