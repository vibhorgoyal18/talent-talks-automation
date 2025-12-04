from __future__ import annotations

from core.web.playwright_wrapper import PlaywrightWrapper


class LoginPage:
    """Page Object for the Login page."""

    PATH = "/login"

    # Playwright selectors (CSS selectors or text selectors)
    USERNAME_FIELD = "#username"
    PASSWORD_FIELD = "#password"
    SUBMIT_BUTTON = "button.radius"
    ERROR_BANNER = "div.flash.error"
    SUCCESS_BANNER = "div.flash.success"

    def __init__(self, wrapper: PlaywrightWrapper, base_url: str) -> None:
        self.wrapper = wrapper
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        """Navigate to the login page."""
        self.wrapper.go_to(f"{self.base_url}{self.PATH}")

    def login(self, username: str, password: str) -> None:
        """Fill in credentials and submit the login form."""
        self.wrapper.type_text(self.USERNAME_FIELD, username)
        self.wrapper.type_text(self.PASSWORD_FIELD, password)
        self.wrapper.click(self.SUBMIT_BUTTON)

    def is_error_displayed(self) -> bool:
        """Check if the error banner is visible."""
        return self.wrapper.is_visible(self.ERROR_BANNER)

    def is_success_displayed(self) -> bool:
        """Check if the success banner is visible."""
        return self.wrapper.is_visible(self.SUCCESS_BANNER)

    def get_error_message(self) -> str:
        """Get the error message text."""
        return self.wrapper.get_text(self.ERROR_BANNER)

    def get_success_message(self) -> str:
        """Get the success message text."""
        return self.wrapper.get_text(self.SUCCESS_BANNER)
