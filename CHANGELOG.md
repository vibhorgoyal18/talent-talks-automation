# Changelog

All notable changes and fixes to this project will be documented in this file.

## [Unreleased]

### Changed
- **2025-12-05**: Switched from Excel (`test_data.xlsx`) to JSON (`test_data.json`) for test data storage - simpler, no external dependency required

### Fixed
- **2025-12-12**: Job description input selector failing - Updated selector from `role=textbox[name='Job Description']` to `role=textbox[name='Enter or paste job description']` in `create_job_opening_page.py`
- **2025-12-05**: URL pattern for dashboard redirect - Changed from `*/dashboard*` to `**/dashboard**` for proper Playwright glob matching
- **2025-12-05**: Invalid login test failing due to email format validation - Updated test data to use valid email format `invalid@test.com`
- **2025-12-05**: Login selectors not found on TalentTalks - Updated `login_page.py` to use role-based selectors: `role=textbox[name='Email Address']`, `role=textbox[name='Password']`, `role=button[name='Sign In']`
- **2025-12-05**: Password read as number from Excel - Added string conversion in `login_steps.py`: `str(row["password"])`
- **2025-12-05**: Valid login test failing (no real credentials) - Marked `valid_login` scenario with `@wip` tag, split into separate scenarios
