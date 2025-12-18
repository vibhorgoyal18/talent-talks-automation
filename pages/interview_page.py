from __future__ import annotations

from core.web.playwright_wrapper import PlaywrightWrapper


class InterviewPage:
    """Page Object for the Interview page (candidate-facing interview interface)."""

    # Interview start indicators
    INTERVIEW_CONTAINER = ".interview-container, #interview-root, [data-testid='interview-page']"
    INTERVIEW_HEADING = "role=heading[name*='Interview']"
    
    # Video/Camera elements
    VIDEO_CONTAINER = "video, .video-container, [data-testid='video']"
    
    # Interview controls
    START_INTERVIEW_BUTTON = "role=button[name*='Start'], role=button[name*='Begin']"
    
    # Interview status indicators
    INTERVIEW_ACTIVE_TEXT = "text=Interview in progress, text=Interview has started, text=Welcome to your interview"
    
    # Common page elements
    CANDIDATE_NAME_DISPLAY = "[data-testid='candidate-name'], .candidate-name"
    TIMER_DISPLAY = "[data-testid='timer'], .timer, .interview-timer"

    def __init__(self, wrapper: PlaywrightWrapper) -> None:
        self.wrapper = wrapper

    def navigate_to(self, url: str) -> None:
        """Navigate to the interview URL."""
        self.wrapper.go_to(url)

    def is_interview_page_loaded(self) -> bool:
        """Check if the interview page is loaded by looking for interview-related elements."""
        try:
            # Check for any of these elements that indicate interview page
            page = self.wrapper.page
            
            # Wait for page to load
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            
            # Check for interview container or heading
            if page.locator(self.INTERVIEW_CONTAINER).first.is_visible(timeout=5000):
                return True
            
            if page.locator(self.INTERVIEW_HEADING).first.is_visible(timeout=5000):
                return True
                
            # Check for video container as fallback
            if page.locator(self.VIDEO_CONTAINER).first.is_visible(timeout=5000):
                return True
            
            return False
        except Exception:
            return False

    def is_interview_started(self) -> bool:
        """Check if the interview has started or is ready to start."""
        try:
            page = self.wrapper.page
            
            # Check if there's a start button (interview ready but not started)
            start_button = page.locator(self.START_INTERVIEW_BUTTON).first
            if start_button.is_visible(timeout=3000):
                return True  # Interview is ready to start
            
            # Check for active interview indicators
            if page.locator(self.INTERVIEW_ACTIVE_TEXT).first.is_visible(timeout=3000):
                return True
            
            # Check for video/camera (indicates interview interface is active)
            if page.locator(self.VIDEO_CONTAINER).first.is_visible(timeout=3000):
                return True
            
            # Check for timer (indicates interview is running)
            if page.locator(self.TIMER_DISPLAY).first.is_visible(timeout=2000):
                return True
            
            return False
        except Exception:
            return False

    def get_page_title(self) -> str:
        """Get the page title."""
        return self.wrapper.page.title()

    def get_current_url(self) -> str:
        """Get the current URL."""
        return self.wrapper.page.url

    def has_interview_parameter(self) -> bool:
        """Check if the URL contains interview-related parameters."""
        url = self.get_current_url()
        return "interview" in url.lower() and ("interviewId" in url or "name" in url)
