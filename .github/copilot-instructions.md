- When adding configuration entries to `.env`, ensure the same keys exist in `.env.example` with safe dummy values so contributors know which variables to provide.
- When making any changes to the framework (structure, utilities, configurations, or core components), update `README.md` to reflect those changes.
- Document any working patterns, conventions, or implementation details in this file (`copilot-instructions.md`) so Copilot understands how to create tests and where to find test data.
- Test data files are located in the `data/` directory. Reference data using `context.data_loader.find_by_key()` in step definitions.
- Step definitions are located in `features/steps/`. Follow the existing pattern using `@given`, `@when`, `@then` decorators from behave.
- Page objects are located in `pages/`. Each page class should accept `wrapper` and `base_url` in the constructor.

## Framework Architecture

```
├── behave.ini                # Behave defaults (formatters, allure)
├── pyproject.toml            # Dependencies + python version
├── .env / .env.example       # Environment config (DEFAULT__*, STAGE__*, etc.)
├── config/                   # Reserved for future shared configs (currently empty)
├── core/
│   ├── web/
│   │   ├── browser_factory.py # Centralized Playwright browser/context creation
│   │   └── playwright_wrapper.py # Higher-level browser actions (click, type, waits)
│   └── reporting/
│       └── allure_manager.py # Helpers to attach screenshots/text/traces to Allure
├── data/
│   └── test_data.xlsx        # Multi-sheet Excel test data (login_data, etc.)
├── docs/
│   ├── configuration.md      # How to manage .env sections
│   ├── dashboard_test_scenarios.md
│   └── e2e_interview_flow.md # End-to-end scenario outline
├── features/
│   ├── environment.py        # Behave hooks: browser, fixtures, Allure attachments
│   ├── login.feature         # Sample feature file
│   └── steps/
│       └── login_steps.py    # Step definitions referencing page objects
├── pages/
│   └── login_page.py         # Page Object Model abstraction
└── utils/
    ├── config_loader.py      # Loads .env namespaces, exposes getters
    ├── data_loader.py        # Excel reader with row lookup helpers
    ├── mail_client.py        # Gmail client for polling interview invitation emails
    └── logger.py             # Shared logger setup (console + report/framework.log)
```

### Execution Layers

| Layer | Responsibility |
|-------|----------------|
| Utils | Configuration, data access, and logging utilities consumed throughout the stack. |
| Core  | Playwright browser/context bootstrap plus reporting glue. Exposed to step definitions. |
| Pages | Page Objects that wrap PlaywrightWrapper interactions and supply meaningful APIs. |
| Features/Steps | Business-readable specs in Gherkin with Python steps orchestrating the flow. |
| Docs  | Living documentation for scenarios, configuration, and E2E planning. |

## Test Writing Guidelines

### 1. Feature Files (Gherkin)
- Place feature files in `features/` directory
- Use meaningful tags: `@ui`, `@smoke`, `@regression`, `@api`
- Follow the pattern:
  ```gherkin
  Feature: <Feature name>
    As a <role>
    I want to <action>
    So that <benefit>

    @ui @smoke
    Scenario Outline: <Descriptive scenario name>
      Given <precondition>
      When <action with "<parameter>">
      Then <expected outcome>

      Examples:
        | parameter | expected_result |
        | value1    | result1         |
  ```

### 2. Step Definitions
- Place in `features/steps/` with naming convention `<feature>_steps.py`
- Use `@given`, `@when`, `@then` decorators from behave
- Access shared objects via `context`:
  - `context.wrapper` - PlaywrightWrapper for browser actions
  - `context.page` - Raw Playwright Page object (if needed)
  - `context.config_loader` - Environment configuration
  - `context.data_loader` - Excel test data access
  - `context.logger` - Logging utility
- Fetch test data using: `context.data_loader.find_by_key("sheet_name", "key_column", "key_value")`
- Attach debug info to Allure: `AllureManager.attach_text("Label", "content")`

```python
from behave import given, when, then
from pages.your_page import YourPage

@given("I open the page")
def step_open_page(context):
    base_url = context.config_loader.get("base_url")
    context.page = YourPage(context.wrapper, base_url)
    context.page.open()

@when("I perform action with \"{param}\"")
def step_action(context, param: str):
    row = context.data_loader.find_by_key("sheet", "scenario", param)
    context.page.do_action(row["field"])

@then("I should see the result")
def step_verify(context):
    assert context.page.is_result_visible(), "Result not visible"
```

### 3. Page Objects
- Place in `pages/` with naming convention `<page_name>_page.py`
- Constructor must accept `wrapper: PlaywrightWrapper` and `base_url: str`
- Define locators as class constants (CSS selectors, text selectors, or XPath)
- Use `self.wrapper` methods: `click()`, `type_text()`, `get_text()`, `is_visible()`, `go_to()`

```python
from core.web.playwright_wrapper import PlaywrightWrapper

class YourPage:
    PATH = "/your-path"
    
    # Playwright selectors (CSS, text, or XPath)
    ELEMENT_SELECTOR = "#element-id"
    BUTTON_SELECTOR = "button.submit"
    LINK_BY_TEXT = "text=Click Here"

    def __init__(self, wrapper: PlaywrightWrapper, base_url: str) -> None:
        self.wrapper = wrapper
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        self.wrapper.go_to(f"{self.base_url}{self.PATH}")

    def do_action(self) -> None:
        self.wrapper.click(self.BUTTON_SELECTOR)
    
    def is_result_visible(self) -> bool:
        return self.wrapper.is_visible(self.ELEMENT_SELECTOR)
```

### 4. Test Data
- Add test data to `data/test_data.xlsx` in appropriate sheets
- Each sheet should have a unique key column (e.g., `scenario`) for lookups
- Access data: `context.data_loader.find_by_key("sheet_name", "key_col", "key_value")`
- Returns a dictionary with column names as keys

### 5. Allure Reporting
- Attach screenshots on failure (automatic via `environment.py`)
- Add custom attachments: `AllureManager.attach_text("name", "content")`
- Add screenshots manually: `AllureManager.attach_screenshot(context.wrapper, "name")`
- Attach Playwright traces: `AllureManager.attach_trace("path/to/trace.zip", "name")`

### 6. Playwright Features
- **Headed mode**: Set `DEFAULT__HEADLESS=false` in `.env`
- **Slow motion**: Set `DEFAULT__SLOW_MO=500` (milliseconds) for debugging
- **Trace recording**: Set `DEFAULT__TRACE=true` to record traces on failure
- **Browser options**: `chromium` (default), `firefox`, `webkit`
- View traces at https://trace.playwright.dev or run `playwright show-trace trace.zip`
