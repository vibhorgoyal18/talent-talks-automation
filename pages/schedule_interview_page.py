from __future__ import annotations

from core.web.playwright_wrapper import PlaywrightWrapper


class ScheduleInterviewPage:
    """Page Object for the Schedule Interview page."""

    PATH = "/interviews/new"

    # Page header
    PAGE_HEADING = "role=heading[name='Schedule New Interview']"
    
    # Job Opening selection
    JOB_OPENING_DROPDOWN = "role=combobox[name='Select Job Opening']"
    
    # Candidate information fields
    CANDIDATE_NAME_INPUT = "role=textbox[name='Candidate Name']"
    CANDIDATE_EMAIL_INPUT = "role=textbox[name='Candidate Email']"
    
    # Date and time selection
    INTERVIEW_DATE_INPUT = "role=textbox[name='Interview Date']"
    INTERVIEW_TIME_INPUT = "role=textbox[name='Interview Time']"
    
    # Action buttons
    SCHEDULE_BUTTON = "role=button[name='Schedule Interview']"
    CANCEL_BUTTON = "role=button[name='Cancel']"
    
    # Success message
    SUCCESS_MESSAGE = "text=Interview scheduled successfully"

    def __init__(self, wrapper: PlaywrightWrapper, base_url: str) -> None:
        self.wrapper = wrapper
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        """Navigate directly to the schedule interview page."""
        self.wrapper.go_to(f"{self.base_url}{self.PATH}")

    def is_loaded(self) -> bool:
        """Check if the page is loaded."""
        return self.wrapper.is_visible(self.PAGE_HEADING, timeout=5000)

    def select_job_opening(self, job_name: str) -> None:
        """Select a job opening from the dropdown."""
        # Click the dropdown to open it
        self.wrapper.click(self.JOB_OPENING_DROPDOWN)
        
        # Wait a bit for dropdown to open
        self.wrapper.page.wait_for_timeout(500)
        
        # Select the option with the job name
        job_option = f"role=option[name='{job_name}']"
        self.wrapper.click(job_option)

    def fill_candidate_name(self, name: str) -> None:
        """Fill in the candidate name."""
        self.wrapper.type_text(self.CANDIDATE_NAME_INPUT, name)

    def fill_candidate_email(self, email: str) -> None:
        """Fill in the candidate email."""
        self.wrapper.type_text(self.CANDIDATE_EMAIL_INPUT, email)



    def select_interview_date(self, date: str) -> None:
        """Select interview date (format: YYYY-MM-DD or MM/DD/YYYY)."""
        self.wrapper.type_text(self.INTERVIEW_DATE_INPUT, date)

    def select_interview_time(self, time: str) -> None:
        """Select interview time (format: HH:MM AM/PM)."""
        self.wrapper.type_text(self.INTERVIEW_TIME_INPUT, time)

    def click_schedule(self) -> None:
        """Click the Schedule Interview button."""
        self.wrapper.click(self.SCHEDULE_BUTTON)

    def is_success_message_displayed(self) -> bool:
        """Check if the success message is displayed or if we navigated away from the form."""
        # Check if we're still on the schedule page
        current_url = self.wrapper.page.url
        
        # If we navigated away, consider it success
        if "/interviews/new" not in current_url:
            return True
            
        # Otherwise check for success message
        return self.wrapper.is_visible(self.SUCCESS_MESSAGE, timeout=2000)

    def schedule_interview(
        self,
        job_name: str,
        candidate_name: str,
        candidate_email: str,
        interview_date: str,
        interview_time: str
    ) -> None:
        """Complete the full interview scheduling flow."""
        self.select_job_opening(job_name)
        self.fill_candidate_name(candidate_name)
        self.fill_candidate_email(candidate_email)
        self.select_interview_date(interview_date)
        self.select_interview_time(interview_time)
        self.click_schedule()
