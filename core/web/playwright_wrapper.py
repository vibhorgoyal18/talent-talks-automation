from __future__ import annotations

from playwright.sync_api import Page, Locator, expect


class PlaywrightWrapper:
    """Provides higher-level helpers on top of Playwright Page."""

    def __init__(self, page: Page, timeout: int = 10000) -> None:
        self.page = page
        self.timeout = timeout  # Playwright uses milliseconds

    def go_to(self, url: str) -> None:
        """Navigate to a URL."""
        self.page.goto(url, wait_until="domcontentloaded")

    def click(self, selector: str) -> None:
        """Click an element by selector."""
        self.page.click(selector, timeout=self.timeout)

    def type_text(self, selector: str, text: str, clear: bool = True) -> None:
        """Type text into an input field and validate it was set successfully."""
        if clear:
            self.page.fill(selector, text, timeout=self.timeout)
        else:
            self.page.locator(selector).press_sequentially(text)
        
        # Validate the value was set successfully
        locator = self.page.locator(selector)
        actual_value = locator.input_value(timeout=2000)
        if actual_value != text:
            raise ValueError(
                f"Failed to set value. Expected: '{text}', but got: '{actual_value}' for selector: {selector}"
            )

    def get_text(self, selector: str) -> str:
        """Get the text content of an element."""
        return self.page.text_content(selector, timeout=self.timeout) or ""

    def get_inner_text(self, selector: str) -> str:
        """Get the inner text of an element."""
        return self.page.inner_text(selector, timeout=self.timeout)

    def is_visible(self, selector: str, timeout: int | None = None) -> bool:
        """Check if an element is visible."""
        try:
            self.page.wait_for_selector(
                selector,
                state="visible",
                timeout=timeout or self.timeout
            )
            return True
        except Exception:
            return False

    def wait_for_selector(self, selector: str, state: str = "visible") -> Locator:
        """Wait for an element to reach a specific state."""
        self.page.wait_for_selector(selector, state=state, timeout=self.timeout)
        return self.page.locator(selector)

    def locator(self, selector: str) -> Locator:
        """Get a locator for an element."""
        return self.page.locator(selector)

    def capture_screenshot(self, file_path: str) -> None:
        """Save a screenshot to a file."""
        self.page.screenshot(path=file_path)

    def get_screenshot_bytes(self) -> bytes:
        """Get screenshot as bytes for Allure attachment."""
        return self.page.screenshot()

    def select_option(self, selector: str, value: str) -> None:
        """Select an option from a dropdown."""
        self.page.select_option(selector, value, timeout=self.timeout)

    def hover(self, selector: str) -> None:
        """Hover over an element."""
        self.page.hover(selector, timeout=self.timeout)

    def wait_for_url(self, url_pattern: str) -> None:
        """Wait for navigation to a URL matching the pattern."""
        self.page.wait_for_url(url_pattern, timeout=self.timeout)

    def wait_for_load_state(self, state: str = "networkidle") -> None:
        """Wait for a specific load state."""
        self.page.wait_for_load_state(state)

    def get_attribute(self, selector: str, attribute: str) -> str | None:
        """Get an attribute value from an element."""
        return self.page.get_attribute(selector, attribute, timeout=self.timeout)

    def is_enabled(self, selector: str) -> bool:
        """Check if an element is enabled."""
        return self.page.is_enabled(selector, timeout=self.timeout)

    def is_checked(self, selector: str) -> bool:
        """Check if a checkbox/radio is checked."""
        return self.page.is_checked(selector, timeout=self.timeout)

    def check(self, selector: str) -> None:
        """Check a checkbox."""
        self.page.check(selector, timeout=self.timeout)

    def uncheck(self, selector: str) -> None:
        """Uncheck a checkbox."""
        self.page.uncheck(selector, timeout=self.timeout)

    def press_key(self, key: str) -> None:
        """Press a keyboard key."""
        self.page.keyboard.press(key)

    def reload(self) -> None:
        """Reload the current page."""
        self.page.reload()

    def go_back(self) -> None:
        """Navigate back."""
        self.page.go_back()

    def go_forward(self) -> None:
        """Navigate forward."""
        self.page.go_forward()

    def get_title(self) -> str:
        """Get the page title."""
        return self.page.title()

    def get_url(self) -> str:
        """Get the current URL."""
        return self.page.url

    def close(self) -> None:
        """Close the page."""
        self.page.close()
