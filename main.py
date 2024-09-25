import time
import sys
from playwright.sync_api import sync_playwright
from utils.telegram import send_telegram_message

COURSE_URL = "https://portalex.technion.ac.il/sap/bc/ui5_ui5/ui2/ushell/shells/abap/FioriLaunchpad.html?sap-client=700&sap-ushell-config=headerless&sap-language=he&appState=lean#AcademicCourse-display"
COURSE_AVAILABILITY_SELECTOR = ".course-status"
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

        # Open the course page (session should be preserved)
        page.goto(COURSE_URL)

        # Keep refreshing until the course is available
        while True:
            print("Checking course availability...")

            # Reload the page
            page.reload()
            # Wait for the page to load
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)

            # Go to Registration Page
            page.click("text='פריטים שנבחרו'")

            # Pick Course
            course_id_element = page.locator(f"text='מק-{course_id}'")
            container = course_id_element.locator('xpath=../../../../../..')
            button = container.locator("button:has(bdi:text-is('הרשם למקצוע'))")
            button.click()

            # Register
            page.click("text='הזמן'")
            page.wait_for_timeout(250)


            full_element = page.locator("text='שגיאה'")

            if full_element.count() > 0:
                print("Course is full")
            else:
                send_telegram_message("Registered Successfully!")
                print("registered successfully!")


            time.sleep(2)  # Wait before refreshing again



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <course_id>")
        sys.exit(1)
    course_id = sys.argv[1]
    connect_to_existing_browser(course_id)
