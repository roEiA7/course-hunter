import time
import sys
from playwright.sync_api import sync_playwright
from utils.telegram import send_telegram_message

COURSE_URL = "https://portalex.technion.ac.il/sap/bc/ui5_ui5/ui2/ushell/shells/abap/FioriLaunchpad.html?sap-client=700&sap-ushell-config=headerless&sap-language=he&appState=lean#AcademicCourse-display"
COURSE_AVAILABILITY_SELECTOR = ".course-status"
def connect_to_existing_browser(course_id, group_id):
    """
    Connects to an existing Chrome session and checks for course availability by refreshing the page.
    Sends a Telegram notification when a course becomes available.
    """
    with sync_playwright() as p:
        # Connect to the existing Chrome session using the remote debugging protocol
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]  # Access the first browser context
        page = context.new_page()

        # Open the course page (session should be preserved)
        page.goto(COURSE_URL)

        # Reload the page
        page.reload()

        # Wait for the page to load
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # Go to Registration Page
        page.click("text='פריטים שנבחרו'")

        # Keep refreshing until the course is available
        while True:
            print("Checking course availability...")


            # Pick Course
            course_id_element = page.locator(f"text='מק-{course_id}'")
            container = course_id_element.locator('xpath=../../../../../..')
            button = container.locator("button:has(bdi:text-is('הרשם למקצוע'))")
            button.click()

            # Pick Group
            selector = f'#__button23-eventPackagesSelectionDialogList-{group_id}'
            page.wait_for_selector(selector, state='visible', timeout=7500)
            page.click(selector)

            # Register
            page.click("text='הזמן'")
            page.wait_for_timeout(250)

            # Check Status
            selector = "text='שגיאה'"
            page.wait_for_selector(selector, state='visible', timeout=5000)
            full_element = page.locator(selector)

            if full_element.count() > 0:
                print("Course is full")

                # Close error message
                selector = "text='סגור'"
                page.wait_for_selector(selector, state='visible', timeout=5000)
                time.sleep(0.5)  # Display Close
                page.click(selector)
                time.sleep(1)  # Wait before retry

            else:
                send_telegram_message("Registered Successfully!")
                print("registered successfully!")
                sys.exit(0)





if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <course_id> <group_number>")
        sys.exit(1)
    course_id = sys.argv[1]
    group_id = sys.argv[2]
    connect_to_existing_browser(course_id, group_id)
