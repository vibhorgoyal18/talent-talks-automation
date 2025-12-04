# End-to-End Interview Flow (Scenario 1)

_Observation date: 02-Dec-2025. Target environment: https://talenttalks.vlinkinfo.com._

## Scenario E2E-01: Candidate completes AI interview from fresh invitation

| Section | Details |
|---------|---------|
| Goal | Validate that a recruiter can create a job opening, schedule an interview for a candidate, deliver the invite email via Mail API, and capture AI interview results with status changes from `Invite Sent` to `Completed`. |
| Actors | Recruiter (web UI), Mail service/API client, Candidate (AI interview participant). |
| Preconditions | Recruiter account with permissions; Mail API credentials for vibhor.goyal@vlinkinfo.com mailbox; candidate device capable of running the AI interview (mic/cam). |
| Data | Job title = `Automation QA Engineer`; Candidate name/email = `qa.bot@example.com`; Slot = current date + 30 min; Interview duration = 20 min. |

### High-Level Flow

1. **Create Job Opening**
   - Navigate to `Create Job Opening`.
   - Populate required fields (name, description, interview duration, evaluation toggles, tech stack) ensuring allocation summary equals 100%.
   - Submit and capture the template ID from success response or Job Openings grid.

2. **Verify Job Opening**
   - Go to `View Job Openings` and search for `Automation QA Engineer`.
   - Assert row displays `ACTIVE` status and zero scheduled interviews initially.

3. **Schedule Interview**
   - Open `Schedule Interview` and select the new job opening.
   - Enter candidate details, slot time, timezone, and enable system checks as required.
   - Upload sample resume/photo if mandatory and submit.
   - Capture interview ID plus initial status (`Invite Sent` with score `N/A`).

4. **Deliver Email via Mail API**
   - Poll the mailbox using the configured Mail API (e.g., Microsoft Graph or IMAP gateway).
   - Locate the invite email for `qa.bot@example.com` and extract the interview launch link.
   - Record pre-interview status via `/interviews` table or API (should be `PENDING / Invite Sent`).

5. **Candidate Takes AI Interview**
   - Launch the extracted link in a fresh browser session (Playwright/selenium) acting as the candidate.
   - Complete required steps: identity verification, system check, AI Q&A (simulate responses), and finish interview.
   - Capture timestamps, AI score, and any attachments produced (recordings, transcript).

6. **Post-Interview Validation**
   - Return to recruiter dashboard `View Interviews` and refresh/filter by candidate.
   - Assert status transitions from `Invite Sent` → `In-progress` (while running) → `Completed` with final stage `REJECTED/SHORTLISTED` per scoring logic.
   - Confirm score field populated (e.g., `47.50% fail`) and action buttons (`View Report`, recordings) enabled.

### Automation Notes

- **Mail API Hook**: Implement a helper in `utils/mail_client.py` to authenticate and fetch recent emails, parse HTML for the CTA button URL, and expose it to Behave steps.
- **Test Data Reset**: Consider deleting the created job opening/interview post-run via API/UI to keep the environment tidy.
- **Synchronization**: Poll interview status via REST (if available) or UI refresh until it reaches `Completed`, with a timeout guard (e.g., 5 minutes).
- **Evidence**: Attach Allure artifacts (screenshots of each milestone, email payload, AI report JSON) for traceability.

### Acceptance Criteria

- Job opening appears in list with `ACTIVE` status immediately after creation.
- Interview row transitions statuses correctly and updates dashboard counters.
- Invite email is received and link launches the candidate interview without manual intervention.
- AI assistant session finishes with a recorded score and accessible report/recordings.
- No errors surfaced in UI logs or API responses throughout the flow.
