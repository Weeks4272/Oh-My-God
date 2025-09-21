from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # Navigate to the local HTML file
    import os
    file_path = os.path.abspath('dna_ai/shadcn-ui/index.html')
    page.goto(f'file://{file_path}')

    # Get the initial number of AI messages
    initial_ai_messages_count = page.locator('.message.ai').count()

    # Type a prompt into the chat input
    page.locator('#mainChatInput').fill('write a python function for fibonacci')

    # Click the send button
    page.locator('#mainSendMessage').click()

    # Wait for the number of AI messages to increase
    expect(page.locator('.message.ai')).to_have_count(initial_ai_messages_count + 1, timeout=30000)

    # Now check the content of the last AI message
    response_locator = page.locator('.message.ai').last
    expect(response_locator).to_contain_text('def fibonacci', timeout=30000)

    # Take a screenshot
    page.screenshot(path='jules-scratch/verification/verification.png')

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
