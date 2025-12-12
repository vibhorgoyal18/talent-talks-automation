from __future__ import annotations

from behave import given, then, when

from core.reporting.allure_manager import AllureManager
from pages.login_page import LoginPage


@given("I open the login page")
def step_open_login_page(context):
    base_url = context.config_loader.get("base_url")
    context.login_page = LoginPage(context.wrapper, base_url)
    context.login_page.open()


@when("I sign in with \"{scenario_name}\"")
def step_sign_in(context, scenario_name: str):
    row = context.data_loader.find_by_key("login_data", "scenario", scenario_name)
    context.last_login_data = row
    # Convert to string in case Excel reads numbers
    email = str(row["username"]) if row["username"] is not None else ""
    password = str(row["password"]) if row["password"] is not None else ""
    context.login_page.login(email, password)
    AllureManager.attach_text("Login data", str(row))


@then("I should see \"{expected_state}\"")
def step_verify_state(context, expected_state: str):
    if expected_state == "success":
        assert context.login_page.is_success_displayed(), "Success banner not visible"
    else:
        assert context.login_page.is_error_displayed(), "Error banner not visible"
