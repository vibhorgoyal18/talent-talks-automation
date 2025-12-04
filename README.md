# TalentTalks Automation Framework

BDD UI automation framework using Behave (Gherkin), Playwright, Allure reporting, and Excel-driven test data. Designed for cross-team collaboration around the TalentTalks hiring platform.

## Tech Stack

- **Language:** Python 3.10+
- **Test Runner:** Behave (Gherkin BDD)
- **Automation:** Playwright with custom wrappers (supports Chromium, Firefox, WebKit)
- **Reporting:** Allure + Playwright Trace Viewer + console logging
- **Data:** `.env` configuration + Excel (`openpyxl`) for scenario data tables

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

## Getting Started

1. **Clone & install deps**
   ```sh
   git clone <repo-url>
   cd talent-talks-automation
   python3 -m venv .venv && source .venv/bin/activate
   pip install playwright allure-behave openpyxl python-dotenv requests behave
   playwright install  # Install browser binaries
   ```
2. **Configure environments**
   ```sh
   cp .env.example .env
   # adjust DEFAULT__* values; export TEST_ENV=stage|prod when needed
   ```
3. **Run a quick test**
   ```sh
   behave features/login.feature
   ```

## Running Tests

- **Run all UI scenarios**
  ```sh
  behave --tags @ui --no-skipped
  ```
- **Run specific feature**
  ```sh
  behave features/login.feature
  ```
- **Headed mode (watch browser)**
  ```sh
  # Set in .env: DEFAULT__HEADLESS=false
  behave features/login.feature
  ```
- **Slow motion debugging**
  ```sh
  # Set in .env: DEFAULT__SLOW_MO=500 (milliseconds)
  behave features/login.feature
  ```
- **Trace recording**
  ```sh
  # Set in .env: DEFAULT__TRACE=true
  # View traces at https://trace.playwright.dev or:
  playwright show-trace report/trace-*.zip
  ```
- **Allure reporting**
  ```sh
  behave -f allure_behave.formatter:AllureFormatter -o allure-results
  allure serve allure-results
  ```

## Data & Configuration Strategy

- `.env` drives runtime configuration. Keys use `ENV__OPTION` syntax (e.g., `STAGE__BASE_URL`). `TEST_ENV` selects the namespace, defaulting to `DEFAULT`.
 - Excel (`data/test_data.xlsx`) stores scenario data. Use `utils.data_loader.ExcelDataLoader` to fetch rows by key for dynamic Behave steps.
 - Gmail utilities live under `utils.mail_client.GmailClient`, reading the `GMAIL_KEY` from `.env` to poll interview invitation emails programmatically.

## Extending the Framework

1. Add new Page Objects under `pages/` wrapping PlaywrightWrapper actions.
2. Create Behave feature files/steps pointing to those page objects.
3. Share cross-cutting helpers via `utils/` and document flows in `docs/`.
4. Keep Allure attachments meaningful (`AllureManager`) to simplify reporting.
5. Use Playwright's trace feature for debugging complex test failures.
6. Integrate cross-channel tools such as the Gmail client when automating invite flows.

---
Contributions welcome—submit issues/PRs for additional flows such as dashboard analytics, interview scheduling, and AI-session validation.
