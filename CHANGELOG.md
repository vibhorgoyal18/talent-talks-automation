# Changelog

All notable changes and fixes to this project will be documented in this file.

## [Unreleased]

### Added
- **2025-12-14**: Created generic, reusable step definitions in `common_steps.py`
  - Generic steps for filling input fields by label: `I fill in "{field_label}" with "{value}"`
  - Generic steps for selecting from dropdowns: `I select "{option}" from "{dropdown_label}"`
  - Generic button click step: `I click the "{button_name}" button`
  - Generic navigation step: `I navigate to "{page_path}" page`
  - Steps for using context/scenario data in fields
  - More atomic, BDD-compliant approach with separate step for each action
- **2025-12-13**: Extended E2E scenario with interview scheduling functionality
  - Created `ScheduleInterviewPage` page object for interview scheduling form
  - Added step definitions for scheduling interviews and email verification
  - Added candidate test data to `test_data.json` for interview scheduling
  - E2E scenario now covers: create job → verify in list → schedule interview → verify email invitation
  - All interview invitations sent to: vibhorgoyal.talenttalks@gmail.com

### Changed
- **2025-12-14**: Refactored interview scheduling steps to be more granular and reusable
  - Replaced monolithic `I schedule an interview...` step with 8 atomic steps
  - Each field fill, dropdown select, and button click is now a separate step
  - Steps accept field labels/button names directly in Gherkin for better readability
  - Old monolithic step marked as DEPRECATED but kept for backward compatibility
- **2025-12-12**: Implemented timestamp-based unique job names to avoid duplicate verification issues
  - Job names now include timestamp: "Job Name - YYYYMMDD_HHMMSS"
  - Updated verification steps to use unique names stored in context
- **2025-12-12**: Consolidated multiple scenarios into single E2E scenario outline with 3 examples
  - Single scenario covers Python, Java, and Frontend developer positions
  - Tags: @ui @job @smoke @e2e
- **2025-12-05**: Switched from Excel (`test_data.xlsx`) to JSON (`test_data.json`) for test data storage - simpler, no external dependency required

### Fixed
- **2025-12-13**: Interview date format - Changed from "MM/DD/YYYY" to "YYYY-MM-DD" for HTML5 date input compatibility
- **2025-12-13**: Interview time format - Changed from "HH:MM AM/PM" to "HH:MM" (24-hour format) for HTML5 time input
- **2025-12-12**: Job opening status verification failing due to duplicate job names from multiple test runs
  - Solution: Appended timestamp to job name to make each test run unique
  - Context storage implemented to pass unique names between steps
- **2025-12-12**: Job opening "Create" button disabled - Fixed by setting resume_evaluation_percentage to 100%
  - Application requires exactly 100% total allocation to enable submit button
  - Updated test data: `enable_resume_evaluation: true`, `resume_evaluation_percentage: 100`
- **2025-12-12**: Job opening selector issues - Fixed by using Playwright's `.filter(has=...)` API instead of `:has()` CSS selector
  - `:has()` CSS syntax doesn't work with Playwright's locator API
  - Changed to: `all_rows.filter(has=page.locator("role=heading[name='...']"))`
- **2025-12-12**: Two "Create Job Opening" buttons causing ambiguity - Changed selector to target form button specifically
  - Updated to: `'form >> role=button[name="Create Job Opening"]'`
- **2025-12-12**: Job description input selector failing - Updated selector from `role=textbox[name='Job Description']` to `role=textbox[name='Enter or paste job description']` in `create_job_opening_page.py`
- **2025-12-05**: URL pattern for dashboard redirect - Changed from `*/dashboard*` to `**/dashboard**` for proper Playwright glob matching
- **2025-12-05**: Invalid login test failing due to email format validation - Updated test data to use valid email format `invalid@test.com`
- **2025-12-05**: Login selectors not found on TalentTalks - Updated `login_page.py` to use role-based selectors: `role=textbox[name='Email Address']`, `role=textbox[name='Password']`, `role=button[name='Sign In']`
- **2025-12-05**: Password read as number from Excel - Added string conversion in `login_steps.py`: `str(row["password"])`
- **2025-12-05**: Valid login test failing (no real credentials) - Marked `valid_login` scenario with `@wip` tag, split into separate scenarios
