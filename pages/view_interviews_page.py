from __future__ import annotations

from core.web.playwright_wrapper import PlaywrightWrapper


class ViewInterviewsPage:
    """Page Object for the View Interviews page."""

    PATH = "/interviews"

    # Page header
    PAGE_HEADING = "role=heading[name='Scheduled Interviews']"
    
    # Search and filters
    SEARCH_INPUT = "role=textbox[name='Search by candidate name or job opening']"
    FILTER_STATUS_DROPDOWN = "role=combobox[name='Filter by status']"
    
    # Interview list table
    INTERVIEWS_TABLE = "role=table"
    TABLE_ROWS = "role=row"
    
    # Action buttons
    VIEW_DETAILS_BUTTON = "role=button[name='View Details']"
    CANCEL_INTERVIEW_BUTTON = "role=button[name='Cancel Interview']"

    def __init__(self, wrapper: PlaywrightWrapper, base_url: str) -> None:
        self.wrapper = wrapper
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        """Navigate directly to the view interviews page."""
        self.wrapper.go_to(f"{self.base_url}{self.PATH}")

    def is_loaded(self) -> bool:
        """Check if the page is loaded."""
        # Wait for either the heading or the table to be visible
        try:
            return (self.wrapper.is_visible(self.PAGE_HEADING, timeout=3000) or 
                    self.wrapper.is_visible(self.INTERVIEWS_TABLE, timeout=3000))
        except Exception:
            return False

    def wait_for_page_load(self) -> None:
        """Wait for the page to fully load."""
        self.wrapper.page.wait_for_load_state("networkidle")
        self.wrapper.page.wait_for_timeout(1000)

    def search_interview(self, search_text: str) -> None:
        """Search for interviews using the search box."""
        if self.wrapper.is_visible(self.SEARCH_INPUT, timeout=2000):
            self.wrapper.type_text(self.SEARCH_INPUT, search_text)
            self.wrapper.page.wait_for_timeout(1000)

    def is_interview_present(self, identifier: str) -> bool:
        """Check if an interview is present in the list by searching for text in any row.
        
        Args:
            identifier: Can be candidate name, job opening name, or any text that appears in the interview row
        
        Returns:
            True if the interview is found, False otherwise
        """
        # First try to search if search is available
        if self.wrapper.is_visible(self.SEARCH_INPUT, timeout=2000):
            self.search_interview(identifier)
        
        # Check if the identifier appears anywhere in the page
        try:
            # Look for text in the table or page content
            return self.wrapper.is_visible(f"text={identifier}", timeout=3000)
        except Exception:
            return False

    def get_interview_status(self, candidate_name: str) -> str | None:
        """Get the status of an interview for a specific candidate.
        
        Args:
            candidate_name: Name of the candidate to find
        
        Returns:
            Status string or None if not found
        """
        # Search for the candidate first
        if self.wrapper.is_visible(self.SEARCH_INPUT, timeout=2000):
            self.search_interview(candidate_name)
        
        # Try to find the status in the row containing the candidate name
        try:
            # Look for common status keywords near the candidate name
            candidate_row = self.wrapper.page.locator(f"role=row:has-text('{candidate_name}')").first
            if candidate_row.is_visible():
                row_text = candidate_row.inner_text()
                # Common status values
                statuses = ["Scheduled", "Completed", "Cancelled", "In Progress", "Pending"]
                for status in statuses:
                    if status.lower() in row_text.lower():
                        return status
            return None
        except Exception:
            return None

    def get_interview_count(self) -> int:
        """Get the total number of interviews visible in the list."""
        try:
            rows = self.wrapper.page.locator(self.TABLE_ROWS).all()
            # Subtract 1 for header row
            return max(0, len(rows) - 1)
        except Exception:
            return 0
