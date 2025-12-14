"""Generic step definitions for common UI interactions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from behave import given, when, then

from features.steps.step_context import StepContext

if TYPE_CHECKING:
    from behave.runner import Context


@when('I navigate to "{page_path}" page')
def step_navigate_to_page(context: Context, page_path: str):
    """Navigate to a specific page path."""
    ctx = StepContext(context)
    full_url = f"{ctx.base_url}{page_path}"
    ctx.wrapper.go_to(full_url)
    ctx.logger.info(f"Navigated to: {full_url}")


@when('I fill in "{field_label}" with "{value}"')
def step_fill_in_field(context: Context, field_label: str, value: str):
    """Fill in a text input field by its label."""
    ctx = StepContext(context)
    
    # Use role-based selector for textbox
    selector = f"role=textbox[name='{field_label}']"
    ctx.wrapper.type_text(selector, value)
    ctx.logger.info(f"Filled in '{field_label}' with '{value}'")


@when('I fill in "{field_label}" with value from scenario "{data_key}"')
def step_fill_in_field_from_data(context: Context, field_label: str, data_key: str):
    """Fill in a field using data from the current scenario data."""
    ctx = StepContext(context)
    
    # Get data from context if it exists
    scenario_data = getattr(context, 'current_scenario_data', {})
    if data_key in scenario_data:
        value = str(scenario_data[data_key])
        selector = f"role=textbox[name='{field_label}']"
        ctx.wrapper.type_text(selector, value)
        ctx.logger.info(f"Filled in '{field_label}' with '{value}' from scenario data")
    else:
        raise ValueError(f"Data key '{data_key}' not found in scenario data")


@when('I select "{option}" from "{dropdown_label}"')
def step_select_from_dropdown(context: Context, option: str, dropdown_label: str):
    """Select an option from a dropdown/combobox by its label."""
    ctx = StepContext(context)
    
    # Click the dropdown to open it
    dropdown_selector = f"role=combobox[name='{dropdown_label}']"
    ctx.wrapper.click(dropdown_selector)
    
    # Wait a bit for dropdown to open
    ctx.wrapper.page.wait_for_timeout(500)
    
    # Select the option
    option_selector = f"role=option[name='{option}']"
    ctx.wrapper.click(option_selector)
    ctx.logger.info(f"Selected '{option}' from '{dropdown_label}'")


@when('I select from "{dropdown_label}" the value stored as "{context_key}"')
def step_select_from_dropdown_context(context: Context, dropdown_label: str, context_key: str):
    """Select an option from a dropdown using a value stored in context."""
    ctx = StepContext(context)
    
    # Get value from context
    option = getattr(context, context_key, None)
    if not option:
        raise ValueError(f"Context key '{context_key}' not found or is empty")
    
    # Click the dropdown to open it
    dropdown_selector = f"role=combobox[name='{dropdown_label}']"
    ctx.wrapper.click(dropdown_selector)
    
    # Wait a bit for dropdown to open
    ctx.wrapper.page.wait_for_timeout(500)
    
    # Select the option
    option_selector = f"role=option[name='{option}']"
    ctx.wrapper.click(option_selector)
    ctx.logger.info(f"Selected '{option}' from '{dropdown_label}' (from context.{context_key})")


@when('I click the "{button_name}" button')
def step_click_button(context: Context, button_name: str):
    """Click a button by its accessible name."""
    ctx = StepContext(context)
    
    selector = f"role=button[name='{button_name}']"
    ctx.wrapper.click(selector)
    ctx.logger.info(f"Clicked button: '{button_name}'")


@then('I should see the "{text}" message')
def step_verify_message(context: Context, text: str):
    """Verify that a specific message is visible on the page."""
    ctx = StepContext(context)
    
    selector = f"text={text}"
    assert ctx.wrapper.is_visible(selector, timeout=5000), \
        f"Message '{text}' is not visible"
    ctx.logger.info(f"Verified message is visible: '{text}'")


@then('the page URL should contain "{url_fragment}"')
def step_verify_url_contains(context: Context, url_fragment: str):
    """Verify that the current URL contains a specific fragment."""
    ctx = StepContext(context)
    
    current_url = ctx.wrapper.page.url
    assert url_fragment in current_url, \
        f"URL '{current_url}' does not contain '{url_fragment}'"
    ctx.logger.info(f"Verified URL contains: '{url_fragment}'")


@when('I wait for {seconds:d} seconds')
def step_wait_seconds(context: Context, seconds: int):
    """Wait for a specified number of seconds."""
    ctx = StepContext(context)
    ctx.wrapper.page.wait_for_timeout(seconds * 1000)
    ctx.logger.info(f"Waited for {seconds} seconds")
