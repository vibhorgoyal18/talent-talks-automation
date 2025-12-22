"""Create a simple interview manually to get a link for TTS testing."""

from playwright.sync_api import sync_playwright
from core.web.playwright_wrapper import PlaywrightWrapper
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.create_job_opening_page import CreateJobOpeningPage
from pages.schedule_interview_page import ScheduleInterviewPage
from utils.config_loader import ConfigLoader
from utils.data_loader import DataLoader
from datetime import datetime, timedelta
import time

config = ConfigLoader()
data_loader = DataLoader()

# Get login credentials
login_data = data_loader.find_by_key("login_data", "scenario", "valid_login")

print("=" * 70)
print("Creating Interview for TTS Testing")
print("=" * 70)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    context = browser.new_context()
    page = context.new_page()
    wrapper = PlaywrightWrapper(page)
    
    base_url = config.get("base_url")
    
    # Login
    print("\n1. Logging in...")
    login_page = LoginPage(wrapper, base_url)
    login_page.open()
    login_page.login(login_data["username"], login_data["password"])
    page.wait_for_timeout(3000)
    print("✅ Logged in")
    
    # Go to dashboard
    print("\n2. Navigating to dashboard...")
    dashboard = DashboardPage(wrapper, base_url)
    dashboard.open()
    page.wait_for_timeout(2000)
    print("✅ On dashboard")
    
    # Click Schedule Interview
    print("\n3. Clicking Schedule Interview...")
    dashboard.click_schedule_interview()
    page.wait_for_timeout(2000)
    
    # Fill interview form
    print("\n4. Filling interview details...")
    schedule_page = ScheduleInterviewPage(wrapper, base_url)
    
    timestamp = datetime.now().strftime("%m%d_%H%M")
    candidate_name = f"TTS_Test_{timestamp}"
    candidate_email = "vibhorgoyal.talenttalks@gmail.com"
    
    # Job and interview time (1 minute from now)
    interview_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
    
    print(f"   Candidate: {candidate_name}")
    print(f"   Email: {candidate_email}")
    print(f"   Time: {interview_time}")
    
    # Select existing job (Python Developer)
    schedule_page.select_job("Python Developer")
    page.wait_for_timeout(1000)
    
    schedule_page.enter_candidate_name(candidate_name)
    schedule_page.enter_candidate_email(candidate_email)
    schedule_page.enter_interview_time(interview_time)
    
    print("\n5. Uploading CV...")
    cv_path = "/Users/vibhorgoyal/PersonalWorkspace/talent-talks-automation/data/test_files/sample_cv.txt"
    schedule_page.upload_cv(cv_path)
    page.wait_for_timeout(1000)
    
    print("\n6. Scheduling interview...")
    schedule_page.click_schedule()
    page.wait_for_timeout(5000)
    
    print("✅ Interview scheduled")
    
    # Wait for email
    print("\n7. Waiting for email (20 seconds)...")
    time.sleep(20)
    
    print("\n8. Fetching interview link from email...")
    from utils.mail_client import GmailIMAPClient
    import re
    
    mail_client = GmailIMAPClient(
        email_address=config.get("gmail_email"),
        app_password=config.get("gmail_app_password")
    )
    mail_client.connect()
    
    messages = mail_client.search_messages(subject="Interview Invitation", max_results=1)
    
    if messages and messages[0].body:
        link_match = re.search(r'https://talenttalks\.vlinkinfo\.com/interview\?[^\s<>"]+', messages[0].body)
        if link_match:
            interview_link = link_match.group(0)
            print(f"\n✅ Interview Link Retrieved:")
            print(f"   {interview_link}")
            print(f"\n📝 Copy this link to test_tts_cdp.py:")
            print(f'INTERVIEW_LINK = "{interview_link}"')
        else:
            print("\n❌ Could not extract link from email")
    else:
        print("\n❌ No email found yet. Check manually.")
    
    mail_client.disconnect()
    
    print("\n" + "=" * 70)
    print("Interview created successfully!")
    print("=" * 70)
    
    print("\nKeeping browser open for 10 seconds...")
    page.wait_for_timeout(10000)
    
    browser.close()
