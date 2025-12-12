from __future__ import annotations

from core.web.playwright_wrapper import PlaywrightWrapper


class LoginPage:
    """Page Object for the TalentTalks Login page."""

    PATH = "/login"

    # Playwright selectors for TalentTalks login page (using role-based selectors)
    EMAIL_FIELD = "role=textbox[name='Email Address']"
    PASSWORD_FIELD = "role=textbox[name='Password']"
    SUBMIT_BUTTON = "role=button[name='Sign In']"
    ERROR_ALERT = "[role='alert']"
    # Success is determined by URL change to dashboard
    DASHBOARD_URL = "/dashboard"

    def __init__(self, wrapper: PlaywrightWrapper, base_url: str) -> None:
        self.wrapper = wrapper
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        """Navigate to the login page."""
        self.wrapper.go_to(f"{self.base_url}{self.PATH}")

    def login(self, email: str, password: str) -> None:
        """Fill in credentials and submit the login form."""
        self.wrapper.type_text(self.EMAIL_FIELD, email)
        self.wrapper.type_text(self.PASSWORD_FIELD, password)
        self.wrapper.click(self.SUBMIT_BUTTON)

    def is_error_displayed(self) -> bool:
        """Check if the error alert is visible."""
        return self.wrapper.is_visible(self.ERROR_ALERT, timeout=3000)

    def is_success_displayed(self) -> bool:
        """Check if login was successful by verifying redirect to dashboard."""
        try:
            # Wait for navigation to dashboard URL
            self.wrapper.wait_for_url(f"**{self.DASHBOARD_URL}**")
            return True
        except Exception:
            return False

    def get_error_message(self) -> str:
        """Get the error message text."""
        return self.wrapper.get_text(self.ERROR_ALERT)

    def get_current_url(self) -> str:
        """Get the current page URL."""
        return self.wrapper.get_url()
