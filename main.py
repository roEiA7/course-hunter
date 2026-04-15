import time
import sys
import random
from playwright.sync_api import sync_playwright
from utils.telegram import send_telegram_message

class CourseRegistrationBot:
    COURSE_URL = "https://portalex.technion.ac.il/sap/bc/ui5_ui5/ui2/ushell/shells/abap/FioriLaunchpad.html?sap-client=700&sap-ushell-config=headerless&sap-language=he&appState=lean#AcademicCourse-display"
    TIMEOUT = 70000

    def __init__(self, course_id):
        self.course_id = course_id
        self.page = None

    def get_available_group_id(self):
        registered_elements = self.page.locator("text='רישום נשמר'")
        max_registration_elements = self.page.locator("text='מקסימום מקומות'")
        
        for i in range(registered_elements.count()):
            r_element = registered_elements.nth(i)
            registered_text = r_element.locator("xpath=./following-sibling::*[2]").inner_text()
            registered_cnt = int(registered_text)

            max_element = max_registration_elements.nth(i)
            max_text = max_element.locator("xpath=./following-sibling::*[2]").inner_text()
            max_cnt = int(max_text)

            if registered_cnt < max_cnt:
                return i
        return None

    def connect_and_setup(self, playwright):
        """Connects to an existing Chrome session and sets up the page."""
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        self.page = context.new_page()
        self.load_catalog()

    def load_catalog(self):
        """Loads the initial catalog page."""
        self.page.goto(self.COURSE_URL)
        self.page.reload()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)
        self.page.click("text='פריטים שנבחרו'")

    def click_course(self):
        """Locates the course and clicks the registration button."""
        print("Checking course availability...")
        try:
            course_id_element = self.page.get_by_text(self.course_id)
            container = course_id_element.locator('xpath=../../../../../..')
            button = container.locator("button:has(bdi:text-is('הרשם למקצוע'))")
            button.click()
            return True
        except Exception as e:
            print(f"Error finding course button: {e}")
            return False

    def order_course(self):
        """Selects a group and clicks order."""
        try:
            self.page.wait_for_selector("#__button32-eventPackagesSelectionDialogList-0", state='visible', timeout=self.TIMEOUT)
            group_id = self.get_available_group_id()
            
            if group_id is None:
                print("No spots available in any group. Canceling...")
                self.page.click("text='בטל'")
                return False
            
            print(f"Available group id: {group_id}")
            self.page.click(f'#__button32-eventPackagesSelectionDialogList-{group_id}')
            self.page.click("text='הזמן'")
            return True
        except Exception as e:
            print(f"Error selecting group: {e}")
            return False

    def handle_result(self):
        """Checks for registration success or error."""
        selector = "text='שגיאה'"
        self.page.wait_for_selector(selector, state='visible', timeout=self.TIMEOUT)
        full_element = self.page.locator(selector)

        if full_element.count() > 0:
            print("Course is full")
            try:
                self.page.wait_for_selector("text='סגור'", state='visible', timeout=self.TIMEOUT)
                time.sleep(0.5)
                self.page.click("text='סגור'", timeout=self.TIMEOUT)
                time.sleep(1)
            except Exception as e:
                print(f"Error closing error message: {e}")
            return False
        else:
            send_telegram_message("Registered Successfully!")
            print("Registered successfully!")
            return True

    def run(self):
        """Main registration loop."""
        with sync_playwright() as p:
            self.connect_and_setup(p)
            while True:
                time.sleep(random.randint(0, 70) / 1000.0)
                if not self.click_course():
                    continue
                
                if not self.order_course():
                    continue
                
                if self.handle_result():
                    break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <course_id>")
        sys.exit(1)

    bot = CourseRegistrationBot(sys.argv[1])
    bot.run()
