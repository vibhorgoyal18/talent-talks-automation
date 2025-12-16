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
    
    # Special handling for buttons that appear in multiple places
    # These buttons appear in both sidebar and form - use form button
    if button_name == "Create Job Opening":
        selector = "form >> role=button[name='Create Job Opening']"
    elif button_name == "Schedule Interview":
        selector = "form >> role=button[name='Schedule Interview']"
    else:
        selector = f"role=button[name='{button_name}']"
    
    ctx.wrapper.click(selector)
    ctx.logger.info(f"Clicked button: '{button_name}'")


@when('I upload the file from "{context_key}" to "{button_label}"')
def step_upload_file(context: Context, context_key: str, button_label: str):
    """Upload a file by directly setting files on the file input element."""
    ctx = StepContext(context)
    
    # Get the file path from context.current_scenario_data
    file_path = context.current_scenario_data.get(context_key)
    if not file_path:
        raise ValueError(f"File path for '{context_key}' not found in context")
    
    # Convert relative path to absolute path
    import os
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine which file input to use based on button label
    if "CV" in button_label or "cv" in button_label.lower():
        # CV file upload (first file input, accepts .pdf)
        file_input = ctx.wrapper.page.locator('input[type="file"][accept=".pdf"]').first
    elif "Image" in button_label or "Photo" in button_label:
        # Image file upload (accepts image types)
        file_input = ctx.wrapper.page.locator('input[type="file"]').nth(1)
    else:
        # Fallback: use first file input
        file_input = ctx.wrapper.page.locator('input[type="file"]').first
    
    # Directly set the file on the input element
    file_input.set_input_files(file_path)
    
    # Wait a moment for the file to be processed
    ctx.wrapper.page.wait_for_timeout(500)
    
    ctx.logger.info(f"Uploaded file '{file_path}' using '{button_label}'")


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


@when('I reload the page')
def step_reload_page(context: Context):
    """Reload the current page."""
    ctx = StepContext(context)
    ctx.wrapper.page.reload(wait_until="networkidle")
    ctx.wrapper.page.wait_for_load_state("networkidle")
    ctx.logger.info("Page reloaded")


@when('I set "{field_label}" to {value:d}')
def step_set_numeric_field(context: Context, field_label: str, value: int):
    """Set a numeric input field (spinbutton) by its label."""
    ctx = StepContext(context)
    
    selector = f"role=spinbutton[name='{field_label}']"
    ctx.wrapper.page.fill(selector, str(value), timeout=ctx.wrapper.timeout)
    ctx.logger.info(f"Set '{field_label}' to {value}")


@when('I check the "{checkbox_label}" checkbox')
def step_check_checkbox(context: Context, checkbox_label: str):
    """Check a checkbox by its label."""
    ctx = StepContext(context)
    
    selector = f"role=checkbox[name='{checkbox_label}']"
    ctx.wrapper.page.check(selector, timeout=ctx.wrapper.timeout)
    ctx.logger.info(f"Checked checkbox: '{checkbox_label}'")


@when('I uncheck the "{checkbox_label}" checkbox')
def step_uncheck_checkbox(context: Context, checkbox_label: str):
    """Uncheck a checkbox by its label."""
    ctx = StepContext(context)
    
    selector = f"role=checkbox[name='{checkbox_label}']"
    ctx.wrapper.page.uncheck(selector, timeout=ctx.wrapper.timeout)
    ctx.logger.info(f"Unchecked checkbox: '{checkbox_label}'")


@then('I should see "{text}" in the page')
def step_verify_text_in_page(context: Context, text: str):
    """Verify that specific text appears anywhere on the page."""
    ctx = StepContext(context)
    
    assert ctx.wrapper.is_visible(f"text={text}", timeout=3000), \
        f"Text '{text}' not found on the page"
    ctx.logger.info(f"Verified text is present: '{text}'")


@then('I should see a heading with "{heading_text}"')
def step_verify_heading(context: Context, heading_text: str):
    """Verify that a heading with specific text is visible."""
    ctx = StepContext(context)
    
    selector = f"role=heading[name='{heading_text}']"
    assert ctx.wrapper.is_visible(selector, timeout=3000), \
        f"Heading '{heading_text}' not found"
    ctx.logger.info(f"Verified heading: '{heading_text}'")


@then('the "{element_type}" with name "{element_name}" should have value "{expected_value}"')
def step_verify_element_value(context: Context, element_type: str, element_name: str, expected_value: str):
    """Verify an element (combobox, textbox, etc.) has a specific value."""
    ctx = StepContext(context)
    
    selector = f"role={element_type}[name='{element_name}']"
    element = ctx.wrapper.page.locator(selector)
    
    # Get the text content or value depending on element type
    if element_type.lower() == "combobox":
        actual_value = element.text_content()
    else:
        actual_value = element.input_value()
    
    assert actual_value == expected_value, \
        f"Expected '{expected_value}' but got '{actual_value}' for {element_type} '{element_name}'"
    ctx.logger.info(f"Verified {element_type} '{element_name}' has value: '{expected_value}'")


@then('I should see the item stored as "{context_key}" in the list')
def step_verify_item_in_list(context: Context, context_key: str):
    """Verify that an item (identified by context key) is visible as a heading in a list."""
    ctx = StepContext(context)
    
    # Get value from context
    item_name = getattr(context, context_key, None)
    if not item_name:
        raise ValueError(f"Context key '{context_key}' not found or is empty")
    
    selector = f"role=heading[name='{item_name}']"
    # Increased timeout to 15 seconds for newly created items that may need backend processing
    assert ctx.wrapper.is_visible(selector, timeout=15000), \
        f"Item '{item_name}' not found in the list"
    ctx.logger.info(f"Verified item is in list: '{item_name}' (from context.{context_key})")


@then('the item stored as "{context_key}" should have status "{expected_status}"')
def step_verify_item_status(context: Context, context_key: str, expected_status: str):
    """Verify that an item has a specific status in a combobox."""
    ctx = StepContext(context)
    
    # Get value from context
    item_name = getattr(context, context_key, None)
    if not item_name:
        raise ValueError(f"Context key '{context_key}' not found or is empty")
    
    # Find the row containing the item heading
    all_rows = ctx.wrapper.page.locator("role=row")
    job_row = all_rows.filter(has=ctx.wrapper.page.locator(f"role=heading[name='{item_name}']"))
    
    # Get the status combobox from that row
    status_locator = job_row.locator("role=combobox")
    
    if status_locator.count() > 0:
        actual_status = status_locator.first.text_content()
        assert actual_status.upper() == expected_status.upper(), \
            f"Expected status '{expected_status}' but got '{actual_status}' for item '{item_name}'"
        ctx.logger.info(f"Verified item '{item_name}' has status: '{expected_status}'")
    else:
        raise AssertionError(f"Could not find status for item '{item_name}'")
