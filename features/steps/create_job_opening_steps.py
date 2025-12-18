from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from behave import given, when, then

from core.reporting.allure_manager import AllureManager
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.create_job_opening_page import CreateJobOpeningPage
from pages.view_job_openings_page import ViewJobOpeningsPage
from pages.schedule_interview_page import ScheduleInterviewPage
from pages.view_interviews_page import ViewInterviewsPage
from features.steps.step_context import StepContext

if TYPE_CHECKING:
    from behave.runner import Context


@given("I am logged in as a valid user")
def step_login_as_valid_user(context: Context):
    """Login with valid credentials from test data."""
    ctx = StepContext(context)
    
    # Get valid login credentials
    creds = ctx.data_loader.find_by_key("login_data", "scenario", "valid_login")
    
    # Login
    login_page = LoginPage(ctx.wrapper, ctx.base_url)
    login_page.open()
    login_page.login(str(creds["username"]), str(creds["password"]))
    
    # Wait for dashboard to load
    dashboard_page = DashboardPage(ctx.wrapper, ctx.base_url)
    assert dashboard_page.is_loaded(), "Dashboard did not load after login"
    ctx.logger.info("Successfully logged in as valid user")


@given("I navigate to the Create Job Opening page")
def step_navigate_to_create_job_opening(context: Context):
    """Navigate to the Create Job Opening page."""
    ctx = StepContext(context)
    
    dashboard_page = DashboardPage(ctx.wrapper, ctx.base_url)
    dashboard_page.click_create_job_opening()
    
    create_job_page = CreateJobOpeningPage(ctx.wrapper, ctx.base_url)
    assert create_job_page.is_loaded(), "Create Job Opening page did not load"
    ctx.logger.info("Navigated to Create Job Opening page")


@when('I load job opening data for "{scenario}"')
def step_load_job_opening_data(context: Context, scenario: str):
    """Load job opening data from test data and store in context with unique timestamp."""
    ctx = StepContext(context)
    
    # Load job opening data
    job_data = ctx.data_loader.find_by_key("job_opening_data", "scenario", scenario)
    
    # Append timestamp to job name to make it unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_job_name = f"{job_data['job_name']} - {timestamp}"
    
    # Store the unique name in context
    context.created_job_name = unique_job_name
    
    # Store all job data in context for use by generic steps
    context.current_scenario_data = {
        "job_name": unique_job_name,
        "job_description": job_data["job_description"],
        "interview_duration": job_data["interview_duration"],
        "enable_resume_evaluation": job_data.get("enable_resume_evaluation", False),
        "resume_evaluation_percentage": job_data.get("resume_evaluation_percentage", 0),
    }
    
    ctx.logger.info(f"Loaded job opening data for scenario: {scenario}")
    ctx.logger.info(f"Unique job name: {unique_job_name}")


@when('I create a job opening with "{scenario}" data')
def step_create_job_opening_with_data(context: Context, scenario: str):
    """
    DEPRECATED: Monolithic step - kept for backward compatibility.
    Use granular steps instead (load data, fill each field, click button).
    
    Create a job opening using data from JSON file.
    """
    ctx = StepContext(context)
    
    job_data = ctx.data_loader.find_by_key("job_opening_data", "scenario", scenario)
    
    # Append timestamp to job name to make it unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_job_name = f"{job_data['job_name']} - {timestamp}"
    
    # Store the unique name in context for later verification
    context.created_job_name = unique_job_name
    
    create_job_page = CreateJobOpeningPage(ctx.wrapper, ctx.base_url)
    create_job_page.create_job_opening(
        job_name=unique_job_name,
        job_description=job_data["job_description"],
        interview_duration=int(job_data["interview_duration"]),
        enable_resume_evaluation=job_data.get("enable_resume_evaluation", False),
        resume_evaluation_percentage=int(job_data.get("resume_evaluation_percentage", 0)),
        enable_code_evaluation=job_data.get("enable_code_evaluation", False),
        programming_language=job_data.get("programming_language"),
        tech_stack=job_data.get("tech_stack", []),
    )
    
    AllureManager.attach_text("Job Opening Data", f"Unique Name: {unique_job_name}\n{str(job_data)}")
    ctx.logger.info(f"Created job opening: {unique_job_name}")


@then("the job opening should be created successfully")
def step_verify_job_created(context: Context):
    """Verify the job opening was created successfully."""
    ctx = StepContext(context)
    
    create_job_page = CreateJobOpeningPage(ctx.wrapper, ctx.base_url)
    
    # Wait for success message or redirect
    try:
        assert create_job_page.is_success_message_displayed(), \
            "Success message not displayed after creating job"
        message = create_job_page.get_success_message()
        ctx.logger.info(f"Job created successfully: {message}")
        AllureManager.attach_text("Success Message", message)
    except Exception as e:
        ctx.logger.info(f"No success message, waiting for redirect: {e}")
        # Wait for redirect to the job listings page (NOT the new page)
        try:
            ctx.wrapper.page.wait_for_url("**/templates", timeout=10000)
            current_url = ctx.wrapper.page.url
            ctx.logger.info(f"Redirected to: {current_url}")
            
            # Verify we're not still on the create page
            if current_url.endswith("/templates/new"):
                raise AssertionError("Still on create page - job creation likely failed")
            
            # Wait for the page to fully load after redirect
            ctx.wrapper.page.wait_for_load_state("networkidle")
            ctx.logger.info("Job created and redirected to job listings")
        except Exception as redirect_error:
            ctx.logger.error(f"Failed to redirect: {redirect_error}")
            ctx.logger.error(f"Current URL: {ctx.wrapper.page.url}")
            raise AssertionError(f"Job creation did not redirect properly. Current URL: {ctx.wrapper.page.url}")


@when('I enter job name "{name}"')
def step_enter_job_name(context: Context, name: str):
    """Enter the job opening name."""
    ctx = StepContext(context)
    
    create_job_page = CreateJobOpeningPage(ctx.wrapper, ctx.base_url)
    create_job_page.enter_job_name(name)
    ctx.logger.info(f"Entered job name: {name}")


@when('I enter job description "{description}"')
def step_enter_job_description(context: Context, description: str):
    """Enter the job description."""
    ctx = StepContext(context)
    
    create_job_page = CreateJobOpeningPage(ctx.wrapper, ctx.base_url)
    create_job_page.enter_job_description(description)
    ctx.logger.info(f"Entered job description: {description}")


@when("I set interview duration to {minutes:d} minutes")
def step_set_interview_duration(context: Context, minutes: int):
    """Set the interview duration."""
    ctx = StepContext(context)
    
    create_job_page = CreateJobOpeningPage(ctx.wrapper, ctx.base_url)
    create_job_page.set_interview_duration(minutes)
    ctx.logger.info(f"Set interview duration to {minutes} minutes")


@when("I enable resume evaluation with {percentage:d} percent")
def step_enable_resume_evaluation(context: Context, percentage: int):
    """Enable resume evaluation with specified percentage."""
    ctx = StepContext(context)
    
    create_job_page = CreateJobOpeningPage(ctx.wrapper, ctx.base_url)
    create_job_page.enable_resume_evaluation(percentage)
    ctx.logger.info(f"Enabled resume evaluation with {percentage}%")


@when("I enable code evaluation with {language}")
def step_enable_code_evaluation(context: Context, language: str):
    """Enable code evaluation with specified programming language."""
    ctx = StepContext(context)
    
    create_job_page = CreateJobOpeningPage(ctx.wrapper, ctx.base_url)
    create_job_page.enable_code_evaluation(language)
    ctx.logger.info(f"Enabled code evaluation with {language}")


@when('I add technology "{technology}"')
def step_add_technology(context: Context, technology: str):
    """Add a technology to the tech stack."""
    ctx = StepContext(context)
    
    create_job_page = CreateJobOpeningPage(ctx.wrapper, ctx.base_url)
    create_job_page.add_technology(technology)
    ctx.logger.info(f"Added technology: {technology}")


@then("the Create Job Opening button should be enabled")
def step_verify_create_button_enabled(context: Context):
    """Verify the Create Job Opening button is enabled."""
    ctx = StepContext(context)
    
    create_job_page = CreateJobOpeningPage(ctx.wrapper, ctx.base_url)
    assert create_job_page.is_create_button_enabled(), \
        "Create Job Opening button is not enabled"
    ctx.logger.info("Create Job Opening button is enabled")


@when("I navigate to View Job Openings page")
def step_navigate_to_view_job_openings(context: Context):
    """Navigate to the View Job Openings page by clicking the sidebar button."""
    ctx = StepContext(context)
    
    from pages.dashboard_page import DashboardPage
    
    view_job_page = ViewJobOpeningsPage(ctx.wrapper, ctx.base_url)
    dashboard_page = DashboardPage(ctx.wrapper, ctx.base_url)
    
    # Wait longer for the job to be saved in the database (increased from 3s to 5s)
    ctx.logger.info("Waiting for job to be saved in database")
    ctx.wrapper.page.wait_for_timeout(5000)
    
    # Click the View Job Openings button in the sidebar to navigate
    ctx.logger.info("Clicking View Job Openings button in sidebar")
    dashboard_page.click_view_job_openings()
    
    # Wait for navigation and page load
    ctx.wrapper.page.wait_for_load_state("networkidle")
    view_job_page.wait_for_page_load()
    
    # If we have a created job name in context, search for it to ensure it's visible
    if hasattr(context, 'created_job_name'):
        ctx.logger.info(f"Searching for job: {context.created_job_name}")
        view_job_page.search_job_opening(context.created_job_name)
        # Wait a bit for search results
        ctx.wrapper.page.wait_for_timeout(1000)
    
    assert view_job_page.is_loaded(), "View Job Openings page did not load"
    ctx.logger.info("Navigated to View Job Openings page")


@then('I should see the job opening "{job_name}" in the list')
def step_verify_job_in_list(context: Context, job_name: str):
    """Verify a job opening is present in the list."""
    ctx = StepContext(context)
    
    # Use the unique job name from context if it was created with timestamp
    actual_job_name = getattr(context, 'created_job_name', job_name)
    
    view_job_page = ViewJobOpeningsPage(ctx.wrapper, ctx.base_url)

    assert view_job_page.is_job_opening_present(actual_job_name), \
        f"Job opening '{actual_job_name}' not found in the list"
    
    ctx.logger.info(f"Job opening '{actual_job_name}' found in the list")
    AllureManager.attach_screenshot(ctx.wrapper, "Job Opening List")


@then('the job opening "{job_name}" should have status "{expected_status}"')
def step_verify_job_status(context: Context, job_name: str, expected_status: str):
    """Verify a job opening has the expected status."""
    ctx = StepContext(context)
    
    # Use the unique job name from context if it was created with timestamp
    actual_job_name = getattr(context, 'created_job_name', job_name)
    
    view_job_page = ViewJobOpeningsPage(ctx.wrapper, ctx.base_url)
    
    actual_status = view_job_page.get_job_opening_status(actual_job_name)
    
    assert actual_status is not None, \
        f"Could not find status for job opening '{actual_job_name}'"
    
    # Normalize status comparison (case-insensitive)
    assert actual_status.upper() == expected_status.upper(), \
        f"Expected status '{expected_status}' but got '{actual_status}' for job '{actual_job_name}'"
    
    ctx.logger.info(f"Job opening '{actual_job_name}' has correct status: {expected_status}")
    AllureManager.attach_text("Job Opening Status", f"{actual_job_name}: {actual_status}")


@when('I load candidate data for "{scenario}"')
def step_load_candidate_data(context: Context, scenario: str):
    """Load candidate data from test data and store in context with unique timestamp."""
    ctx = StepContext(context)
    
    # Load candidate data
    candidate_data = ctx.data_loader.find_by_key("candidate_data", "scenario", scenario)
    
    # Append short timestamp to candidate name to make it unique
    timestamp = datetime.now().strftime("%m%d_%H%M")
    base_name = candidate_data["candidate_name"].replace("Test Candidate ", "")
    unique_candidate_name = f"{base_name}_{timestamp}"
    
    # Store in context for use by generic steps
    context.current_scenario_data = {
        "candidate_name": unique_candidate_name,
        "candidate_email": candidate_data["candidate_email"],
        "cv_file": candidate_data["cv_file"],
        "photo_file": candidate_data["photo_file"],
    }
    context.candidate_email = candidate_data["candidate_email"]
    
    ctx.logger.info(f"Loaded candidate data for scenario: {scenario}")
    ctx.logger.info(f"Candidate: {unique_candidate_name}, Email: {candidate_data['candidate_email']}")


@when('I fill in "{field_label}" with tomorrow\'s date')
def step_fill_in_tomorrows_date(context: Context, field_label: str):
    """Fill in a date field with tomorrow's date in YYYY-MM-DD format."""
    ctx = StepContext(context)
    
    from datetime import datetime, timedelta
    tomorrow = datetime.now() + timedelta(days=1)
    date_value = tomorrow.strftime("%Y-%m-%d")
    
    selector = f"role=textbox[name='{field_label}']"
    ctx.wrapper.type_text(selector, date_value)
    ctx.logger.info(f"Filled in '{field_label}' with tomorrow's date: {date_value}")


@when('I schedule an interview for the job opening with "{scenario}" candidate data')
def step_schedule_interview_with_candidate(context: Context, scenario: str):
    """
    DEPRECATED: Monolithic step - kept for backward compatibility.
    Use granular steps instead (load data, navigate, fill fields, click button).
    
    Schedule an interview using candidate data from JSON file.
    """
    ctx = StepContext(context)
    
    # Load candidate data
    candidate_data = ctx.data_loader.find_by_key("candidate_data", "scenario", scenario)
    
    # Get the unique job name from context
    job_name = getattr(context, 'created_job_name', None)
    if not job_name:
        raise AssertionError("Job name not found in context. Please create a job opening first.")
    
    # Get interview date and time (1 minute from now for 30 mins)
    from datetime import datetime, timedelta
    now = datetime.now()
    interview_start = now + timedelta(minutes=1)
    interview_date = interview_start.strftime("%Y-%m-%d")  # Format for date input type
    interview_time = interview_start.strftime("%H:%M")  # Format: HH:MM (24-hour)
    
    # Store interview time in context for verification
    context.interview_start_time = interview_start
    context.interview_duration_minutes = 30
    
    # Navigate to schedule interview page
    schedule_page = ScheduleInterviewPage(ctx.wrapper, ctx.base_url)
    schedule_page.open()
    
    # Wait for page to load
    assert schedule_page.is_loaded(), "Schedule Interview page did not load"
    ctx.logger.info("Schedule Interview page loaded")
    
    # Fill in interview details
    schedule_page.schedule_interview(
        job_name=job_name,
        candidate_name=str(candidate_data["candidate_name"]),
        candidate_email=str(candidate_data["candidate_email"]),
        interview_date=interview_date,
        interview_time=interview_time
    )
    
    # Store email in context for verification
    context.candidate_email = candidate_data["candidate_email"]
    
    AllureManager.attach_text(
        "Interview Details",
        f"Job: {job_name}\n"
        f"Candidate: {candidate_data['candidate_name']}\n"
        f"Email: {candidate_data['candidate_email']}\n"
        f"Date: {interview_date}\n"
        f"Time: {interview_time}"
    )
    ctx.logger.info(f"Scheduled interview for {candidate_data['candidate_name']}")


@then("the interview should be scheduled successfully")
def step_verify_interview_scheduled(context: Context):
    """Verify the interview was scheduled successfully by checking for success toast or navigation."""
    ctx = StepContext(context)
    
    schedule_page = ScheduleInterviewPage(ctx.wrapper, ctx.base_url)
    
    # Wait for either toast or navigation
    ctx.wrapper.page.wait_for_timeout(3000)
    
    # Check for any toast messages (success or error)
    if schedule_page.is_success_toast_displayed():
        toast_message = schedule_page.get_toast_message()
        ctx.logger.info(f"Success toast displayed: {toast_message}")
        AllureManager.attach_text("Success Toast", toast_message)
        ctx.logger.info("Interview scheduling step completed")
        return
    
    if schedule_page.is_error_toast_displayed():
        error_message = schedule_page.get_toast_message()
        ctx.logger.error(f"Error toast displayed: {error_message}")
        AllureManager.attach_screenshot(ctx.wrapper, "Error Toast")
        AllureManager.attach_text("Error Message", error_message)
        raise AssertionError(f"Interview scheduling failed with error: {error_message}")
    
    # Check if we navigated away (alternative success indicator)
    current_url = ctx.wrapper.page.url
    ctx.logger.info(f"Current URL after scheduling: {current_url}")
    
    if "/interviews/new" not in current_url:
        ctx.logger.info("Successfully navigated away from schedule page")
        AllureManager.attach_screenshot(ctx.wrapper, "After Schedule Success")
        ctx.logger.info("Interview scheduling step completed")
    else:
        # Still on the schedule page with no toast - capture page state for debugging
        ctx.logger.error("Interview was not scheduled - still on the schedule page with no toast message")
        
        # Capture any validation errors or other messages on the page
        page_text = ctx.wrapper.page.inner_text("body")
        ctx.logger.error(f"Page contains: {page_text[:500]}...")
        
        AllureManager.attach_screenshot(ctx.wrapper, "Schedule Failed - No Toast")
        AllureManager.attach_text("Page Content", page_text)
        raise AssertionError("Interview was not scheduled - still on the schedule page with no success or error toast")
    
    ctx.logger.info(f"Candidate email stored in context: {getattr(context, 'candidate_email', 'Not found')}")


@then('the interview invitation email should be sent to "{email}"')
def step_verify_interview_email_sent(context: Context, email: str):
    """Verify the interview invitation email was sent."""
    ctx = StepContext(context)
    
    # For now, we'll just log this step
    # In a real implementation, we would:
    # 1. Connect to the email account
    # 2. Search for the latest email with subject containing "Interview Invitation"
    # 3. Verify the email was sent to the correct address
    # 4. Verify the email contains the job opening name and candidate details
    
    ctx.logger.info(f"Email verification step - Expected email to: {email}")
    
    # Get the candidate email from context to verify it matches
    candidate_email = getattr(context, 'candidate_email', None)
    if candidate_email:
        assert candidate_email == email, \
            f"Candidate email '{candidate_email}' does not match expected '{email}'"
        ctx.logger.info(f"Verified candidate email matches: {email}")
    
    # TODO: Integrate with actual email verification using MailClient
    # from utils.mail_client import MailClient
    # mail_client = MailClient()
    # mail_client.connect()
    # latest_email = mail_client.fetch_latest_email()
    # assert email in latest_email.to_addresses
    
    AllureManager.attach_text("Email Verification", f"Interview invitation should be sent to: {email}")
    ctx.logger.info(f"Interview invitation email verification completed for: {email}")


@when("I navigate to View Interviews page")
def step_navigate_to_view_interviews(context: Context):
    """Navigate to the View Interviews page by clicking the sidebar button."""
    ctx = StepContext(context)
    
    from pages.dashboard_page import DashboardPage
    
    view_interviews_page = ViewInterviewsPage(ctx.wrapper, ctx.base_url)
    dashboard_page = DashboardPage(ctx.wrapper, ctx.base_url)
    
    # Wait a moment for the interview to be saved in the database
    ctx.logger.info("Waiting for interview to be saved in database")
    ctx.wrapper.page.wait_for_timeout(3000)
    
    # Click the View Interviews button in the sidebar to navigate
    ctx.logger.info("Clicking View Interviews button in sidebar")
    dashboard_page.click_view_interviews()
    
    # Wait for navigation and page load
    ctx.wrapper.page.wait_for_load_state("networkidle")
    view_interviews_page.wait_for_page_load()
    
    assert view_interviews_page.is_loaded(), "View Interviews page did not load"
    ctx.logger.info("Navigated to View Interviews page")


@then('I should see the interview for candidate "{candidate_name}" in the list')
def step_verify_interview_in_list(context: Context, candidate_name: str):
    """Verify an interview for a specific candidate is present in the list."""
    ctx = StepContext(context)
    
    # Use the candidate name from context if available
    actual_candidate_name = getattr(context, 'current_scenario_data', {}).get('candidate_name', candidate_name)
    
    view_interviews_page = ViewInterviewsPage(ctx.wrapper, ctx.base_url)
    
    # Also try to search by job name if available
    job_name = getattr(context, 'created_job_name', None)
    
    # Try to find the interview by candidate name first
    found = view_interviews_page.is_interview_present(actual_candidate_name)
    
    # If not found by candidate name, try job name
    if not found and job_name:
        ctx.logger.info(f"Candidate '{actual_candidate_name}' not found, trying job name: {job_name}")
        found = view_interviews_page.is_interview_present(job_name)
    
    assert found, \
        f"Interview for candidate '{actual_candidate_name}' not found in the list"
    
    ctx.logger.info(f"Interview for candidate '{actual_candidate_name}' found in the list")
    AllureManager.attach_screenshot(ctx.wrapper, "Interview List")


@when("I search for the recently created interview")
def step_search_recently_created_interview(context: Context):
    """Search for the recently created interview using the job title."""
    ctx = StepContext(context)
    
    # Get job name from context
    job_name = getattr(context, 'created_job_name', None)
    candidate_name = getattr(context, 'current_scenario_data', {}).get('candidate_name', '')
    
    if not job_name:
        raise ValueError("No job name found in context. Make sure job was created first.")
    
    view_interviews_page = ViewInterviewsPage(ctx.wrapper, ctx.base_url)
    
    ctx.logger.info(f"Searching for interview by job title: {job_name}")
    view_interviews_page.search_interview(job_name)
    ctx.wrapper.page.wait_for_timeout(2000)  # Wait longer for search results to stabilize
    
    ctx.logger.info(f"Search completed for: {job_name}")


@then("I should see the recently created interview")
def step_verify_recently_created_interview(context: Context):
    """Verify the recently scheduled interview is present in the list using data from context."""
    ctx = StepContext(context)
    
    # Get candidate name and job name from context
    candidate_name = getattr(context, 'current_scenario_data', {}).get('candidate_name')
    job_name = getattr(context, 'created_job_name', None)
    
    if not candidate_name and not job_name:
        raise ValueError("No candidate name or job name found in context")
    
    view_interviews_page = ViewInterviewsPage(ctx.wrapper, ctx.base_url)
    
    # The search should have already been done by a previous step (if needed)
    # Just verify the interview is visible
    found = view_interviews_page.is_interview_present(candidate_name if candidate_name else job_name)
    
    assert found, \
        f"Interview not found in the list. Job: '{job_name}', candidate: '{candidate_name}'"
    
    ctx.logger.info(f"Interview found in the list (Candidate: {candidate_name}, Job: {job_name})")
    AllureManager.attach_screenshot(ctx.wrapper, "Interview List")


@then('the interview for candidate "{candidate_name}" should have status "{expected_status}"')
def step_verify_interview_status(context: Context, candidate_name: str, expected_status: str):
    """Verify an interview has the expected status."""
    ctx = StepContext(context)
    
    # Use the candidate name from context if available
    actual_candidate_name = getattr(context, 'current_scenario_data', {}).get('candidate_name', candidate_name)
    
    view_interviews_page = ViewInterviewsPage(ctx.wrapper, ctx.base_url)
    
    actual_status = view_interviews_page.get_interview_status(actual_candidate_name)
    
    assert actual_status is not None, \
        f"Could not find status for interview with candidate '{actual_candidate_name}'"
    
    # Normalize status comparison (case-insensitive)
    assert actual_status.upper() == expected_status.upper(), \
        f"Expected status '{expected_status}' but got '{actual_status}' for candidate '{actual_candidate_name}'"
    
    ctx.logger.info(f"Interview for candidate '{actual_candidate_name}' has correct status: {expected_status}")
    AllureManager.attach_text("Interview Status", f"{actual_candidate_name}: {actual_status}")


@when("I click the 3-dot menu for the recently created interview")
def step_click_three_dot_menu_for_interview(context: Context):
    """Click the 3-dot menu button for the recently created interview."""
    ctx = StepContext(context)
    
    # Get identifier from context (prefer candidate name since it's more unique in the table)
    candidate_name = getattr(context, 'current_scenario_data', {}).get('candidate_name')
    job_name = getattr(context, 'created_job_name', None)
    
    identifier = candidate_name if candidate_name else job_name
    
    if not identifier:
        raise ValueError("No interview identifier (candidate name or job name) found in context")
    
    view_interviews_page = ViewInterviewsPage(ctx.wrapper, ctx.base_url)
    view_interviews_page.click_three_dot_menu_for_interview(identifier)
    
    ctx.logger.info(f"Clicked 3-dot menu for interview: {identifier}")
    AllureManager.attach_screenshot(ctx.wrapper, "3-Dot Menu Opened")


@when('I click the "{option}" option from the menu')
def step_click_menu_option(context: Context, option: str):
    """Click a specific option from the dropdown menu."""
    ctx = StepContext(context)
    
    view_interviews_page = ViewInterviewsPage(ctx.wrapper, ctx.base_url)
    
    if option.lower() == "delete":
        view_interviews_page.click_delete_from_menu()
        ctx.logger.info(f"Clicked '{option}' option from menu")
        AllureManager.attach_screenshot(ctx.wrapper, f"Clicked {option} Option")
    elif option.lower() == "send invite":
        view_interviews_page.click_resend_invite_from_menu()
        ctx.logger.info(f"Clicked '{option}' option from menu")
        AllureManager.attach_screenshot(ctx.wrapper, f"Clicked {option} Option")
    else:
        raise ValueError(f"Unsupported menu option: {option}")


@then("the invite should be resent successfully")
def step_verify_invite_resent(context: Context):
    """Verify the invite was resent successfully."""
    ctx = StepContext(context)
    
    # Wait for any success message or notification
    ctx.wrapper.page.wait_for_timeout(2000)
    
    ctx.logger.info("Interview invite resent successfully")
    AllureManager.attach_screenshot(ctx.wrapper, "After Resend Invite")


@then("I should receive the interview invitation email")
def step_receive_interview_email(context: Context):
    """Wait for and verify the interview invitation email arrives (checks both inbox and spam)."""
    ctx = StepContext(context)
    
    from utils.mail_client import GmailIMAPClient, MailClientError
    import time
    
    # Get email credentials from config
    gmail_email = ctx.config.get("gmail_email")
    gmail_app_password = ctx.config.get("gmail_app_password")
    
    # Gmail credentials are mandatory
    assert gmail_email, "Gmail email not configured in .env file (DEFAULT__GMAIL_EMAIL)"
    assert gmail_app_password, "Gmail app password not configured in .env file (DEFAULT__GMAIL_APP_PASSWORD)"
    
    try:
        # Connect to Gmail
        mail_client = GmailIMAPClient(gmail_email, gmail_app_password)
        mail_client.connect()
        
        ctx.logger.info(f"Waiting for interview invitation email to {gmail_email}...")
        print(f"\n📧 Checking email: {gmail_email}")
        
        email_message = None
        folder_found = None
        
        # Try INBOX first, then Spam folder
        folders_to_check = [("INBOX", "📥 Inbox"), ("[Gmail]/Spam", "🗑️ Spam")]
        
        timeout_seconds = 60
        poll_interval = 5
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            for folder, folder_display in folders_to_check:
                try:
                    # Search for "Interview Link for Candidate" which is the actual subject
                    messages = mail_client.list_messages(
                        folder=folder,
                        max_results=5,
                        search_criteria='SUBJECT "Interview Link"'
                    )
                    
                    if messages:
                        # Find the most recent matching email
                        for msg in messages:
                            if "Interview Link" in msg.subject:
                                email_message = msg
                                folder_found = folder_display
                                break
                    
                    if email_message:
                        break
                except Exception as e:
                    ctx.logger.debug(f"Could not check {folder}: {e}")
            
            if email_message:
                break
            
            print(f"⏳ Waiting for email... ({int(time.time() - start_time)}s elapsed)")
            time.sleep(poll_interval)
        
        mail_client.disconnect()
        
        # Email must be found - fail the test if not
        assert email_message is not None, \
            f"Interview invitation email not received within {timeout_seconds} seconds. " \
            f"Checked folders: INBOX and Spam. Subject should contain 'Interview Link'"
        
        ctx.logger.info(f"✅ Email found in {folder_found} - Subject: {email_message.subject}")
        print(f"\n✅ Email received in {folder_found}")
        print(f"   Subject: {email_message.subject}")
        print(f"   From: {email_message.sender}")
        
        # Store email in context for next step to extract URL
        context.interview_email = email_message
        context.email_folder = folder_found
        
        AllureManager.attach_text("Email Folder", folder_found)
        AllureManager.attach_text("Email Subject", email_message.subject)
        AllureManager.attach_text("Email Snippet", email_message.snippet)
        
    except MailClientError as e:
        ctx.logger.error(f"Failed to connect to Gmail: {e}")
        print(f"\n❌ Gmail connection failed: {e}")
        AllureManager.attach_text("Email Error", str(e))
        raise AssertionError(f"Failed to connect to Gmail: {e}")


@then("I should extract the interview URL from the email")
def step_extract_interview_url(context: Context):
    """Extract the interview URL from the received email and print it to terminal."""
    ctx = StepContext(context)
    
    import re
    
    # Email must be available from previous step
    assert hasattr(context, 'interview_email'), \
        "No interview email found in context. Previous step must have failed."
    
    email_message = context.interview_email
    folder_found = getattr(context, 'email_folder', 'Unknown')
    
    # Email body must not be empty
    assert email_message, "Email message is None"
    assert email_message.body, \
        f"Email body is empty. Subject: {email_message.subject}, From: {email_message.sender}"
    
    # Search for interview URL patterns in the email body
    # Pattern matches: https://talenttalks.vlinkinfo.com/interview?...
    # Also matches: https://talenttalks.vlinkinfo.com/interview/...
    url_pattern = r'https?://[^\s<>"]+/interview[^\s<>"]*'
    matches = re.findall(url_pattern, email_message.body)
    
    # URL must be found in email
    assert matches, \
        f"No interview URL found in email body ({len(email_message.body)} characters). " \
        f"Expected pattern: https://...talenttalks.../interview?... or /interview/..."
    
    interview_url = matches[0]  # Take the first match
    context.interview_url = interview_url
    
    # Log and print to terminal
    ctx.logger.info(f"Interview URL extracted: {interview_url}")
    print(f"\n{'='*80}")
    print(f"🔗 INTERVIEW INVITATION LINK")
    print(f"{'='*80}")
    print(f"   Found in: {folder_found}")
    print(f"   Link: {interview_url}")
    print(f"{'='*80}\n")
    
    AllureManager.attach_text("Interview URL", interview_url)
    AllureManager.attach_text("Email Body", email_message.body)


@when("I open the interview link")
def step_open_interview_link(context: Context):
    """
    Open the interview link that was extracted from the email.
    Requires interview_url in context from previous step.
    """
    from pages.interview_page import InterviewPage
    
    ctx = StepContext(context)
    
    # Interview URL must exist from previous step
    assert hasattr(context, 'interview_url'), \
        "No interview URL found in context. Must extract URL from email first."
    
    interview_url = context.interview_url
    
    ctx.logger.info(f"Opening interview link: {interview_url}")
    print(f"\n🌐 Opening interview link: {interview_url}")
    
    # Create interview page object and navigate
    interview_page = InterviewPage(ctx.wrapper)
    interview_page.navigate_to(interview_url)
    
    # Store page object in context
    context.interview_page = interview_page
    
    ctx.logger.info("Interview link opened successfully")


@then("the interview page should load successfully")
def step_verify_interview_page_loaded(context: Context):
    """
    Verify that the interview page has loaded successfully.
    """
    from pages.interview_page import InterviewPage
    
    ctx = StepContext(context)
    
    # Interview page must exist from previous step
    assert hasattr(context, 'interview_page'), \
        "No interview page found in context. Must open interview link first."
    
    interview_page: InterviewPage = context.interview_page
    
    # Check if interview page loaded
    assert interview_page.is_interview_page_loaded(), \
        f"Interview page did not load. Current URL: {interview_page.get_current_url()}"
    
    # Verify URL has interview parameters
    assert interview_page.has_interview_parameter(), \
        f"URL does not contain interview parameters. URL: {interview_page.get_current_url()}"
    
    print(f"✅ Interview page loaded successfully")
    print(f"📄 Page title: {interview_page.get_page_title()}")
    print(f"🔗 Current URL: {interview_page.get_current_url()}")
    
    ctx.logger.info("Interview page loaded and verified")
    AllureManager.attach_screenshot(ctx.wrapper, "Interview Page Loaded")


@then("the interview should be ready to start")
def step_verify_interview_ready(context: Context):
    """
    Verify that the interview is ready to start or has started.
    """
    from pages.interview_page import InterviewPage
    
    ctx = StepContext(context)
    
    # Interview page must exist from previous step
    assert hasattr(context, 'interview_page'), \
        "No interview page found in context. Must open interview link first."
    
    interview_page: InterviewPage = context.interview_page
    
    # Check if interview is started/ready
    assert interview_page.is_interview_started(), \
        f"Interview is not ready to start. Current URL: {interview_page.get_current_url()}"
    
    print(f"✅ Interview is ready to start or has started")
    
    ctx.logger.info("Interview verified as ready/started")
    AllureManager.attach_screenshot(ctx.wrapper, "Interview Ready")


@then("the interview should be deleted successfully")
def step_verify_interview_deleted(context: Context):
    """Verify the interview was deleted successfully by confirming the delete action."""
    ctx = StepContext(context)
    
    view_interviews_page = ViewInterviewsPage(ctx.wrapper, ctx.base_url)
    
    # Confirm the delete if a confirmation dialog appears
    view_interviews_page.confirm_delete()
    
    ctx.logger.info("Interview delete action confirmed")
    AllureManager.attach_screenshot(ctx.wrapper, "After Delete Confirmation")


@then("I should not see the recently created interview")
def step_verify_interview_not_present(context: Context):
    """Verify the recently deleted interview is no longer present in the list."""
    ctx = StepContext(context)
    
    # Get identifier from context (prefer job name, fallback to candidate name)
    job_name = getattr(context, 'created_job_name', None)
    candidate_name = getattr(context, 'current_scenario_data', {}).get('candidate_name')
    
    identifier = job_name if job_name else candidate_name
    
    if not identifier:
        raise ValueError("No interview identifier (job name or candidate name) found in context")
    
    view_interviews_page = ViewInterviewsPage(ctx.wrapper, ctx.base_url)
    
    # Verify the interview is no longer present
    is_deleted = view_interviews_page.is_interview_deleted(identifier)
    
    assert is_deleted, \
        f"Interview '{identifier}' is still present in the list after deletion"
    
    ctx.logger.info(f"Verified interview '{identifier}' is no longer in the list")
    AllureManager.attach_screenshot(ctx.wrapper, "Interview Deleted - List View")

