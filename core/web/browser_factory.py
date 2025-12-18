from __future__ import annotations

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright

from utils.config_loader import ConfigLoader


class BrowserFactory:
    """Creates Playwright browser instances based on configuration."""

    def __init__(self, config: ConfigLoader) -> None:
        self._config = config
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    def _get_browser_options(self) -> dict:
        """Build browser launch options from config."""
        headless = self._config.get("headless", "false").lower() == "true"
        slow_mo = self._config.get_int("slow_mo", 0)

        options = {
            "headless": headless,
            "slow_mo": slow_mo,
            "args": [
                "--use-fake-ui-for-media-stream",  # Auto-accept media permissions
                "--use-fake-device-for-media-stream",  # Use fake camera/microphone
                "--auto-select-desktop-capture-source=Entire screen",  # Auto-select entire screen
                "--enable-usermedia-screen-capturing",  # Enable screen capture
                "--allow-http-screen-capture",  # Allow screen capture over HTTP
                "--disable-features=UserMediaCaptureOnFocus",  # Don't require focus
            ],
        }

        return options

    def _get_context_options(self) -> dict:
        """Build browser context options from config."""
        return {
            "viewport": {"width": 1920, "height": 1080},
            "ignore_https_errors": True,
            # Note: display-capture is handled via browser args, not context permissions
        }

    def create_browser(self) -> tuple[Playwright, Browser, BrowserContext, Page]:
        """Create and return Playwright browser, context, and page.
        
        Returns:
            Tuple of (playwright, browser, context, page) for proper cleanup.
        """
        browser_type = self._config.get("browser", "chromium").lower()
        browser_options = self._get_browser_options()
        context_options = self._get_context_options()

        # Start Playwright
        self._playwright = sync_playwright().start()

        # Launch browser based on config
        if browser_type == "firefox":
            self._browser = self._playwright.firefox.launch(**browser_options)
        elif browser_type == "webkit":
            self._browser = self._playwright.webkit.launch(**browser_options)
        else:
            # Default to Chromium (includes Chrome, Edge)
            self._browser = self._playwright.chromium.launch(**browser_options)

        # Create context and page
        self._context = self._browser.new_context(**context_options)
        
        # Enable tracing if configured
        if self._config.get("trace", "false").lower() == "true":
            self._context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page = self._context.new_page()

        return self._playwright, self._browser, self._context, page

    def close(self, save_trace_path: str | None = None) -> None:
        """Close browser and cleanup resources."""
        if self._context:
            if save_trace_path and self._config.get("trace", "false").lower() == "true":
                self._context.tracing.stop(path=save_trace_path)
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
