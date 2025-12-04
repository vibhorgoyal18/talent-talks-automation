from __future__ import annotations

from pathlib import Path

from behave import fixture, use_fixture

from core.reporting.allure_manager import AllureManager
from core.web.browser_factory import BrowserFactory
from core.web.playwright_wrapper import PlaywrightWrapper
from utils.config_loader import get_config
from utils.data_loader import ExcelDataLoader
from utils.logger import get_logger

ROOT = Path(__file__).resolve().parents[1]


@fixture
def playwright_browser(context):
    """Fixture to create Playwright browser, context, and page for each scenario."""
    config = context.config_loader
    factory = BrowserFactory(config)
    playwright, browser, browser_context, page = factory.create_browser()
    
    timeout_ms = config.get_int("timeout", 10) * 1000  # Convert to milliseconds
    wrapper = PlaywrightWrapper(page, timeout=timeout_ms)
    
    context.playwright = playwright
    context.browser = browser
    context.browser_context = browser_context
    context.page = page
    context.wrapper = wrapper
    context.browser_factory = factory
    
    yield wrapper
    
    # Save trace if enabled and scenario failed
    trace_path = None
    if config.get("trace", "false").lower() == "true" and hasattr(context, "scenario_failed"):
        trace_path = str(ROOT / "report" / f"trace-{context.scenario_name}.zip")
    
    factory.close(save_trace_path=trace_path)


def before_all(context):
    """Setup before all scenarios."""
    context.logger = get_logger()
    context.config_loader = get_config()
    context.data_loader = ExcelDataLoader(ROOT / "data" / "test_data.xlsx")
    context.base_url = context.config_loader.get("base_url")


def before_scenario(context, scenario):
    """Setup before each scenario."""
    context.scenario_name = scenario.name.replace(" ", "_")
    use_fixture(playwright_browser, context)
    context.logger.info("Starting scenario: %s", scenario.name)


def after_scenario(context, scenario):
    """Cleanup after each scenario."""
    if scenario.status == "failed":
        context.scenario_failed = True
        AllureManager.attach_screenshot(context.wrapper, f"failed-{scenario.name}")
        if hasattr(scenario, "exception") and scenario.exception:
            AllureManager.attach_text("Scenario failure", str(scenario.exception))
    context.logger.info("Finished scenario: %s - Status: %s", scenario.name, scenario.status)
