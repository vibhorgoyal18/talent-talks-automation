# TalentTalks Dashboard Test Scenarios

_Environment observed on 02-Dec-2025 using account `vibhor.goyal@vlinkinfo.com`._

## 1. Authentication & Session

| ID | Scenario | Preconditions | Steps | Expected Result |
|----|----------|---------------|-------|-----------------|
| AUTH-01 | Valid login redirects to dashboard | User logged out on `/login` | Enter valid email/password and click `Sign In` | User lands on `/dashboard` showing sidebar (Overview, Create/View Job Opening, Schedule/View Interviews) and profile summary |
| AUTH-02 | Invalid login shows inline validation | User logged out | Enter valid email + incorrect password, submit | Error banner appears, user remains on login form |
| AUTH-03 | Logout clears session | User logged in anywhere in console | Click `Logout` button in sidebar | Session terminates, browser returns to marketing homepage with Login CTA |

## 2. Dashboard Overview Widgets

| ID | Scenario | Preconditions | Steps | Expected Result |
|----|----------|---------------|-------|-----------------|
| DASH-01 | Metrics align with backend counts | At least one interview and job opening exists | Compare card values: `Interviews Scheduled Today`, `Proctoring Alerts`, `Job Openings` (Active/In-active/On-hold/Closed), `Interviews` (Scheduled/Completed/In-progress), `Candidates Overview` (Invited/Interviewed/Shortlisted plus benchmark tiles) against API/DB | UI values match data source, zero states rendered as `0` |
| DASH-02 | Widget navigation | Dashboard loaded | Click `Proctoring Alerts` or other cards | Appropriate detail view (alerts table, interviews list, etc.) opens, preserving breadcrumbs |
| DASH-03 | Empty states | No ongoing interviews scheduled | `On-going Interviews` table displays "No ongoing interviews at the moment" message |

## 3. Job Openings List (`/templates`)

| ID | Scenario | Preconditions | Steps | Expected Result |
|----|----------|---------------|-------|-----------------|
| JOB-01 | Global search | Multiple job openings present | Use search box to query by title, description, tech stack, date | Table filters rows to those containing query in selected "Search In" scope |
| JOB-02 | Status dropdown update | Any opening in `ACTIVE` state | Toggle status combobox to `INACTIVE` then back | Status persists (API call succeeds), row badge updates with toast confirmation |
| JOB-03 | Row actions | Opening listed | Click `Schedule Interview`, `Edit`, `Clone`, `Delete` | Each CTA routes to correct page or prompts confirmation (delete) |
| JOB-04 | Pagination/infinite scroll | >10 openings exist | Scroll to bottom or navigate pages | Additional rows load or pagination controls appear without layout shift |

## 4. Create Job Opening (`/templates/new`)

| ID | Scenario | Preconditions | Steps | Expected Result |
|----|----------|---------------|-------|-----------------|
| CJO-01 | Required field validation | Form open | Leave `Job Opening Name`, `Job Description`, `Interview Duration` empty and submit | Inline errors shown, submit button disabled until resolved |
| CJO-02 | Skill generation helper | Description populated | Click `Generate Skills` | Suggested skills appear or are injected into description/tech stack |
| CJO-03 | Evaluation toggles | Form open | Toggle Resume/Static Questions/Code Evaluation | Allocation summary updates percentages; warning persists until total = 100% |
| CJO-04 | Tech stack management | Form open | Add technology via input + `Add`, then `Edit Tech Stack` | Chips/list updates, edit dialog allows reordering/removal |
| CJO-05 | Successful creation | All required fields valid, allocation = 100% | Submit | User redirected to Job Openings table; new row shows `ACTIVE` with correct counts |

## 5. Schedule Interview (`/interviews/new`)

| ID | Scenario | Preconditions | Steps | Expected Result |
|----|----------|---------------|-------|-----------------|
| SCH-01 | Template dependency | At least one job opening `ACTIVE` | Leave `Select Job Opening` empty and attempt to proceed | Field marked required, scheduling blocked |
| SCH-02 | Candidate details validation | Form open | Provide invalid email / blank fields | Inline validation prevents submission |
| SCH-03 | Advanced evaluation toggles | Template selected | Toggle Resume/Static/Code/Second Camera/System Check | Allocation progress updates; 100% rule enforced |
| SCH-04 | File uploads | Form open | Use `Select CV File` and `Select Image` | Accepts PDF for resume and JPG/PNG for avatar, shows filenames |
| SCH-05 | Timezone handling | Candidate details entered | Change timezone combobox | Date/time preview recalculates or validation ensures compatibility |

## 6. Interviews List (`/interviews`)

| ID | Scenario | Preconditions | Steps | Expected Result |
|----|----------|---------------|-------|-----------------|
| INT-01 | Search & filter | Interviews exist across statuses | Use search to filter by candidate/email/job/date | Table narrows results; "Search In" scope honored |
| INT-02 | Status transitions | Row currently `PENDING`/`REJECTED` etc. | Change combobox value | Status persists and KPIs (dashboard counts) update accordingly |
| INT-03 | Action buttons | Interview row available | Trigger `Manage Notes`, `Edit`, `Delete`, `Download Resume`, `Send Invite`, `View Report`, `View Cam-1/2 Recording` | Each action opens corresponding modal/page, download triggers file, recordings open player |
| INT-04 | Invite flow | Row with `Invite Sent` stage | Click `Send Invite` | System re-sends email, toast confirmation shown |
| INT-05 | Completed interview report | Completed row with score (e.g., 26.67% fail) | Click `View Report` | Detailed AI analysis page loads with sections for resume, coding, static questions |

## 7. Candidate Analytics Integrity

| ID | Scenario | Preconditions | Steps | Expected Result |
|----|----------|---------------|-------|-----------------|
| CAN-01 | Benchmarks derived from interview data | Completed interviews with Above/Below Benchmark values | Compare counts (Above=0, Below=19, Rejected=0 as observed) to aggregated scores | Dashboard reflects actual counts |
| CAN-02 | Shortlist workflow | Candidate shortlisted from interviews | Changing interview status to `SHORTLISTED` increments `Shortlisted` metric | Metric updates within dashboard refresh |

## 8. General UX & Security

| ID | Scenario | Description | Expected Result |
|----|----------|-------------|-----------------|
| UX-01 | Sidebar navigation persistence | Navigate between Overview, Job Openings, Schedule, Interviews | Sidebar remains fixed with active state indicator |
| UX-02 | Session timeout | Remain idle until token expiry | User prompted to log in again; unsaved changes warned |
| SEC-01 | Direct URL access control | Logged out user tries `/dashboard`, `/templates` etc. | Redirected to `/login` |
| SEC-02 | Role-based visibility | Use account with limited permissions (if available) | Buttons like `Delete Job Opening` hidden or disabled appropriately |

> These scenarios can feed Behave feature files (login, job_openings, interviews) and Pytest smoke suites verifying API/DB consistency.
