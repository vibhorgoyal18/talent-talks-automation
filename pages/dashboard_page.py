from __future__ import annotations

from core.web.playwright_wrapper import PlaywrightWrapper


class DashboardPage:
    """Page Object for the TalentTalks Dashboard page."""

    PATH = "/dashboard"

    # Navigation buttons
    OVERVIEW_BUTTON = "role=button[name='Overview']"
    CREATE_JOB_OPENING_BUTTON = "role=button[name='Create Job Opening']"
    VIEW_JOB_OPENINGS_BUTTON = "role=button[name='View Job Openings']"
    SCHEDULE_INTERVIEW_BUTTON = "role=button[name='Schedule Interview']"
    VIEW_INTERVIEWS_BUTTON = "role=button[name='View Interviews']"
    USER_MANAGEMENT_BUTTON = "role=button[name='User Management']"
    LOGOUT_BUTTON = "role=button[name='Logout']"

    # Dashboard indicators
    DASHBOARD_HEADING = "role=heading[name='Dashboard Overview']"
    JOB_OPENINGS_HEADING = "role=heading[name='Job Openings']"

    def __init__(self, wrapper: PlaywrightWrapper, base_url: str) -> None:
        self.wrapper = wrapper
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        """Navigate to the dashboard page."""
        self.wrapper.go_to(f"{self.base_url}{self.PATH}")

    def is_loaded(self) -> bool:
        """Check if dashboard is loaded."""
        return self.wrapper.is_visible(self.DASHBOARD_HEADING, timeout=5000)

    def click_create_job_opening(self) -> None:
        """Click on Create Job Opening button."""
        self.wrapper.click(self.CREATE_JOB_OPENING_BUTTON)

    def click_view_job_openings(self) -> None:
        """Click on View Job Openings button."""
        self.wrapper.click(self.VIEW_JOB_OPENINGS_BUTTON)

    def click_schedule_interview(self) -> None:
        """Click on Schedule Interview button."""
        self.wrapper.click(self.SCHEDULE_INTERVIEW_BUTTON)

    def click_view_interviews(self) -> None:
        """Click on View Interviews button."""
        self.wrapper.click(self.VIEW_INTERVIEWS_BUTTON)

    def click_user_management(self) -> None:
        """Click on User Management button."""
        self.wrapper.click(self.USER_MANAGEMENT_BUTTON)

    def logout(self) -> None:
        """Click on Logout button."""
        self.wrapper.click(self.LOGOUT_BUTTON)
