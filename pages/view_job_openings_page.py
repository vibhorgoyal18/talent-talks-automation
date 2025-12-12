from __future__ import annotations

from typing import Optional

from core.web.playwright_wrapper import PlaywrightWrapper


class ViewJobOpeningsPage:
    """Page Object for the View Job Openings page."""

    PATH = "/templates"

    # Page header
    PAGE_HEADING = "role=heading[name='Job Openings']"
    CREATE_JOB_BUTTON = "role=button[name='Create New Job Opening']"

    # Filter tabs
    ALL_TAB = "role=button[name='All']"
    ACTIVE_TAB = "role=button[name='Active']"
    INACTIVE_TAB = "role=button[name='Inactive']"
    ON_HOLD_TAB = "role=button[name='On Hold']"
    CLOSED_TAB = "role=button[name='Closed']"

    # Search and filters
    SEARCH_INPUT = "role=textbox[name='Search job openings']"
    FILTER_BUTTON = "role=button[name='Filter']"

    # Table
    JOB_OPENINGS_TABLE = "role=table"

    def __init__(self, wrapper: PlaywrightWrapper, base_url: str) -> None:
        self.wrapper = wrapper
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        """Navigate directly to the view job openings page."""
        self.wrapper.go_to(f"{self.base_url}{self.PATH}")

    def is_loaded(self) -> bool:
        """Check if the page is loaded."""
        return self.wrapper.is_visible(self.PAGE_HEADING, timeout=5000)

    def wait_for_page_load(self) -> None:
        """Wait for the page to be fully loaded."""
        self.wrapper.wait_for_selector(self.JOB_OPENINGS_TABLE, state="visible")

    def search_job_opening(self, job_name: str) -> None:
        """Search for a job opening by name."""
        self.wrapper.type_text(self.SEARCH_INPUT, job_name)

    def is_job_opening_present(self, job_name: str) -> bool:
        """Check if a job opening is present in the list."""
        # Look for the job name as a heading in the table cell
        job_selector = f"role=heading[name='{job_name}']"
        return self.wrapper.is_visible(job_selector, timeout=3000)

    def get_job_opening_status(self, job_name: str) -> Optional[str]:
        """Get the status of a specific job opening.
        
        Args:
            job_name: Name of the job opening
            
        Returns:
            Status string (ACTIVE, IN-ACTIVE, ON-HOLD, CLOSED) or None if not found
        """
        # First, ensure the job opening exists
        if not self.is_job_opening_present(job_name):
            return None
        
        try:
            # Find the row containing the job name
            # The status is in a combobox in the Status column
            row_locator = self.wrapper.page.locator(f"role=row:has(role=heading[name='{job_name}'])")
            if row_locator.count() == 0:
                return None
            
            # Get the status combobox from that row
            status_cell = row_locator.locator("role=cell >> role=combobox").first
            if status_cell.count() > 0:
                status_text = status_cell.inner_text()
                return status_text.strip()
            
            return None
        except Exception as e:
            return None

    def click_job_opening(self, job_name: str) -> None:
        """Click on a job opening to view details."""
        job_link = f"role=link[name='{job_name}']"
        self.wrapper.click(job_link)

    def filter_by_status(self, status: str) -> None:
        """Filter job openings by status.
        
        Args:
            status: One of 'All', 'Active', 'Inactive', 'On Hold', 'Closed'
        """
        status_tab_map = {
            "All": self.ALL_TAB,
            "Active": self.ACTIVE_TAB,
            "Inactive": self.INACTIVE_TAB,
            "On Hold": self.ON_HOLD_TAB,
            "Closed": self.CLOSED_TAB,
        }
        
        tab_selector = status_tab_map.get(status)
        if tab_selector:
            self.wrapper.click(tab_selector)

    def get_job_openings_count(self) -> int:
        """Get the total number of job openings displayed."""
        # Count rows in the table (excluding header)
        rows_selector = f"{self.JOB_OPENINGS_TABLE} >> role=row"
        return self.wrapper.locator(rows_selector).count() - 1  # Subtract header row

    def click_create_new_job(self) -> None:
        """Click the Create New Job Opening button."""
        self.wrapper.click(self.CREATE_JOB_BUTTON)
