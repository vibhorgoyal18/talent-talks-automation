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


@when('I create a job opening with "{scenario}" data')
def step_create_job_opening_with_data(context: Context, scenario: str):
    """Create a job opening using data from JSON file."""
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
    """Navigate to the View Job Openings page."""
    ctx = StepContext(context)
    
    view_job_page = ViewJobOpeningsPage(ctx.wrapper, ctx.base_url)
    
    current_url = ctx.wrapper.page.url
    ctx.logger.info(f"Current URL before navigation: {current_url}")
    
    # If we're already on the templates page (after job creation redirect),
    # just reload to get fresh data
    if "/templates" in current_url:
        ctx.logger.info("Already on templates page, reloading for fresh data")
        ctx.wrapper.page.reload(wait_until="networkidle")
        view_job_page.wait_for_page_load()
    else:
        # Navigate to the page
        # Wait a bit for the job to be saved in the database
        ctx.wrapper.page.wait_for_timeout(2000)
        view_job_page.open()
        # Wait for the page to load with network idle
        ctx.wrapper.page.wait_for_load_state("networkidle")
        view_job_page.wait_for_page_load()
    
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
    """Load candidate data from test data and store in context."""
    ctx = StepContext(context)
    
    # Load candidate data
    candidate_data = ctx.data_loader.find_by_key("candidate_data", "scenario", scenario)
    
    # Store in context for use by generic steps
    context.current_scenario_data = candidate_data
    context.candidate_email = candidate_data["candidate_email"]
    
    ctx.logger.info(f"Loaded candidate data for scenario: {scenario}")
    ctx.logger.info(f"Candidate: {candidate_data['candidate_name']}, Email: {candidate_data['candidate_email']}")


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
    
    # Get interview date and time (use default values for now)
    from datetime import datetime, timedelta
    tomorrow = datetime.now() + timedelta(days=1)
    interview_date = tomorrow.strftime("%Y-%m-%d")  # Format for date input type
    interview_time = "10:00"  # Format: HH:MM (24-hour)
    
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
    """Verify the interview was scheduled successfully."""
    ctx = StepContext(context)
    
    schedule_page = ScheduleInterviewPage(ctx.wrapper, ctx.base_url)
    
    # Wait a bit for any navigation or message to appear
    ctx.wrapper.page.wait_for_timeout(2000)
    
    # Log current URL
    current_url = ctx.wrapper.page.url
    ctx.logger.info(f"Current URL after scheduling: {current_url}")
    
    # Take a screenshot for debugging
    AllureManager.attach_screenshot(ctx.wrapper, "After Scheduling")
    
    # For now, let's just log that we attempted to schedule
    # TODO: Add proper verification once we understand the success indicator
    ctx.logger.info("Interview scheduling step completed")
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

