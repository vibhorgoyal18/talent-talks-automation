"""Quick script to create a test interview and get the link."""

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from utils.config_loader import ConfigLoader
from utils.data_loader import JsonDataLoader
from core.web.playwright_wrapper import PlaywrightWrapper
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.schedule_interview_page import ScheduleInterviewPage
import datetime

load_dotenv()

def create_quick_interview():
    """Create a quick interview and return the link."""
    
    config = ConfigLoader()
    data_loader = JsonDataLoader("data/test_data.json")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            wrapper = PlaywrightWrapper(page)
            base_url = config.get("base_url")
            
            # Login
            print("1. Logging in...")
            login_page = LoginPage(wrapper, base_url)
            login_page.open()
            
            login_data = data_loader.find_by_key("login_data", "scenario", "valid_login")
            login_page.login(login_data["username"], login_data["password"])
            page.wait_for_timeout(3000)
            print("✅ Logged in")
            
            # Navigate to schedule interview
            print("\n2. Navigating to Schedule Interview...")
            dashboard = DashboardPage(wrapper, base_url)
            dashboard.click_schedule_interview()
            page.wait_for_timeout(2000)
            print("✅ On schedule interview page")
            
            # Fill interview details
            print("\n3. Filling interview details...")
            schedule_page = ScheduleInterviewPage(wrapper, base_url)
            
            # Get candidate data
            candidate_data = data_loader.find_by_key("candidate_data", "scenario", "python_developer")
            
            # Add timestamp to make unique
            timestamp = datetime.datetime.now().strftime("%m%d_%H%M")
            unique_name = f"TestCandidate_{timestamp}"
            
            # Fill form
            schedule_page.select_job_opening(candidate_data["job_opening"])
            schedule_page.fill_candidate_name(unique_name)
            schedule_page.fill_candidate_email(candidate_data["email"])
            schedule_page.upload_resume("data/test_files/sample_cv.txt")
            page.wait_for_timeout(1000)
            
            # Set interview to now
            schedule_page.set_interview_to_now()
            page.wait_for_timeout(1000)
            
            print("✅ Form filled")
            
            # Schedule
            print("\n4. Scheduling interview...")
            schedule_page.click_schedule_interview()
            page.wait_for_timeout(5000)
            print("✅ Interview scheduled")
            
            # Get the link
            print("\n5. Getting interview link...")
            interview_link = schedule_page.get_interview_invitation_link()
            
            if interview_link:
                print("\n" + "=" * 60)
                print("✅ INTERVIEW LINK GENERATED:")
                print(interview_link)
                print("=" * 60)
                
                # Save to file for easy access
                with open("/tmp/latest_interview_link.txt", "w") as f:
                    f.write(interview_link)
                print("\n💾 Link saved to: /tmp/latest_interview_link.txt")
                
                return interview_link
            else:
                print("❌ Could not get interview link")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            print("\nClosing browser in 5 seconds...")
            page.wait_for_timeout(5000)
            browser.close()

if __name__ == "__main__":
    link = create_quick_interview()
    if link:
        print(f"\n\nUse this link: {link}")
    else:
        print("\nFailed to create interview")
