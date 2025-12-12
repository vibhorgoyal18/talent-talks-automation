from __future__ import annotations

from typing import TYPE_CHECKING

from behave import given, when, then

from core.reporting.allure_manager import AllureManager
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.create_job_opening_page import CreateJobOpeningPage
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
    
    create_job_page = CreateJobOpeningPage(ctx.wrapper, ctx.base_url)
    create_job_page.create_job_opening(
        job_name=job_data["job_name"],
        job_description=job_data["job_description"],
        interview_duration=int(job_data["interview_duration"]),
        enable_resume_evaluation=job_data.get("enable_resume_evaluation", False),
        resume_evaluation_percentage=int(job_data.get("resume_evaluation_percentage", 0)),
        enable_code_evaluation=job_data.get("enable_code_evaluation", False),
        programming_language=job_data.get("programming_language"),
        tech_stack=job_data.get("tech_stack", []),
    )
    
    AllureManager.attach_text("Job Opening Data", str(job_data))
    ctx.logger.info(f"Created job opening: {job_data['job_name']}")


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
    except Exception:
        ctx.wrapper.wait_for_url("**/templates**")
        ctx.logger.info("Redirected to job listings after creation")


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
