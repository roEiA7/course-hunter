import time
import sys
from playwright.sync_api import sync_playwright
from utils.telegram import send_telegram_message

COURSE_URL = "https://portalex.technion.ac.il/sap/bc/ui5_ui5/ui2/ushell/shells/abap/FioriLaunchpad.html?sap-client=700&sap-ushell-config=headerless&sap-language=he&appState=lean#AcademicCourse-display"
REGISTERED_THRESHOLD_MAIN = 58
REGISTERED_THRESHOLD = 57

def get_available_group_id(page):
    registered_elements = page.locator("text='רישום נשמר'")
    for i in range(registered_elements.count()):
        element = registered_elements.nth(i)
        registered_text = element.locator("xpath=./following-sibling::*[2]").inner_text()
        registered_cnt = int(registered_text)

        if i == 0 and registered_cnt < REGISTERED_THRESHOLD_MAIN:
            return 0
        if registered_cnt < REGISTERED_THRESHOLD:
            return i
    return 0

def connect_to_existing_browser(course_id):
    """
    Connects to an existing Chrome session and checks for course availability by refreshing the page.
    Sends a Telegram notification when a course becomes available.
    """
    with sync_playwright() as p:
        # Connect to the existing Chrome session using the remote debugging protocol
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]  # Access the first browser context
        page = context.new_page()

        # Load SAP
        page.goto(COURSE_URL)
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        page.click("text='פריטים שנבחרו'")

        # Keep refreshing until the course is available
        while True:
            print("Checking course availability...")

            # Pick Course
            try:
                course_id_element = page.locator(f"text='מק-{course_id}'")
                container = course_id_element.locator('xpath=../../../../../..')
                button = container.locator("button:has(bdi:text-is('הרשם למקצוע'))")
                button.click()
            except Exception as e:
                print(f"Error finding course button: {e}")
                continue

            # Pick Group & Register
            try:
                page.wait_for_selector("#__button23-eventPackagesSelectionDialogList-0", state='visible', timeout=10000)
                group_id = get_available_group_id(page)
                page.click(f'#__button23-eventPackagesSelectionDialogList-{group_id}')
                page.click("text='הזמן'")
                page.wait_for_timeout(250)
            except Exception as e:
                print(f"Error selecting group: {e}")
                continue

            # Check Registration Status
            selector = "text='שגיאה'"
            page.wait_for_selector(selector, state='visible', timeout=5000)
            full_element = page.locator(selector)

            if full_element.count() > 0:
                print("Course is full")
                try:
                    # Close error message
                    page.wait_for_selector("text='סגור'", state='visible', timeout=5000)
                    time.sleep(0.5)
                    page.click("text='סגור'", timeout=5000)
                    time.sleep(1)
                except Exception as e:
                    print(f"Error closing error message: {e}")
            else:
                send_telegram_message("Registered Successfully!")
                print("Registered successfully!")
                sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <course_id>")
        sys.exit(1)

    connect_to_existing_browser(sys.argv[1])