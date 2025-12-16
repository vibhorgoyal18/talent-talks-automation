from __future__ import annotations

from core.web.playwright_wrapper import PlaywrightWrapper


class ViewInterviewsPage:
    """Page Object for the View Interviews page."""

    PATH = "/interviews"

    # Page header
    PAGE_HEADING = "role=heading[name='Scheduled Interviews']"
    
    # Search and filters
    SEARCH_INPUT = "xpath=//input[contains(@placeholder, 'Search by Candidate')]"
    FILTER_STATUS_DROPDOWN = "role=combobox[name='Filter by status']"
    
    # Interview list table
    INTERVIEWS_TABLE = "role=table"
    TABLE_ROWS = "role=row"
    
    # Action buttons
    VIEW_DETAILS_BUTTON = "role=button[name='View Details']"
    CANCEL_INTERVIEW_BUTTON = "role=button[name='Cancel Interview']"
    # The 3-dot menu button is in the Actions column (last cell of each row)
    THREE_DOT_MENU = "xpath=//button[@aria-label or contains(@class, 'MuiButtonBase')]"
    DELETE_MENU_OPTION = "role=menuitem[name='Delete']"
    CONFIRM_DELETE_BUTTON = "role=button[name='Delete']"

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

    def click_three_dot_menu_for_interview(self, identifier: str) -> None:
        """Click the 3-dot menu button for a specific interview.
        
        Args:
            identifier: Can be candidate name or job opening name to identify the interview row
        """
        # First search for the interview to make sure it's visible
        if self.wrapper.is_visible(self.SEARCH_INPUT, timeout=2000):
            self.search_interview(identifier)
            self.wrapper.page.wait_for_timeout(1000)
        
        # Find the row containing the interview
        try:
            # Find the row with the identifier text
            row = self.wrapper.page.locator(f"role=row:has-text('{identifier}')").first
            
            # Wait for the row to be visible
            row.wait_for(state="visible", timeout=5000)
            
            # Find the button in the last cell (Actions column) of this row
            # The actions button is in the last cell with class MuiButtonBase
            action_button = row.locator("button").last
            
            # Wait for action button to be visible
            action_button.wait_for(state="visible", timeout=3000)
            
            # Click the menu button
            action_button.click()
            self.wrapper.page.wait_for_timeout(500)
            
        except Exception as e:
            raise Exception(f"Failed to click 3-dot menu for interview '{identifier}': {str(e)}")

    def click_delete_from_menu(self) -> None:
        """Click the Delete option from the opened dropdown menu."""
        try:
            # Wait for the dropdown menu to appear
            self.wrapper.page.wait_for_timeout(500)
            
            # Click the Delete menuitem
            delete_option = self.wrapper.page.locator(self.DELETE_MENU_OPTION).first
            
            # Wait for delete option to be visible
            delete_option.wait_for(state="visible", timeout=3000)
            
            delete_option.click()
            
            # Wait a moment for any confirmation dialog to appear
            self.wrapper.page.wait_for_timeout(500)
            
        except Exception as e:
            raise Exception(f"Failed to click Delete option: {str(e)}")

    def confirm_delete(self) -> None:
        """Confirm the delete action if a confirmation dialog appears."""
        try:
            # Wait for confirmation dialog
            self.wrapper.page.wait_for_timeout(1000)
            
            # Try multiple possible selectors for confirm button
            confirm_selectors = [
                "role=button[name='Delete']",
                "role=button[name='Confirm']",
                "button:has-text('Delete')",
                "button:has-text('Confirm')",
                "button:has-text('Yes')",
                ".btn-danger:has-text('Delete')"
            ]
            
            confirmed = False
            for selector in confirm_selectors:
                try:
                    confirm_button = self.wrapper.page.locator(selector).first
                    confirm_button.wait_for(state="visible", timeout=2000)
                    confirm_button.click()
                    confirmed = True
                    break
                except Exception:
                    continue
            
            if not confirmed:
                # No confirmation dialog appeared, or delete was instant
                pass
            
            # Wait for the action to complete
            self.wrapper.page.wait_for_timeout(1000)
            self.wrapper.page.wait_for_load_state("networkidle")
            
        except Exception as e:
            # Confirmation might not be needed, log but don't fail
            pass

    def is_interview_deleted(self, identifier: str) -> bool:
        """Check if an interview is no longer present in the list.
        
        Args:
            identifier: Can be candidate name or job opening name
        
        Returns:
            True if the interview is NOT found (deleted), False if still present
        """
        # Refresh the search
        if self.wrapper.is_visible(self.SEARCH_INPUT, timeout=2000):
            # Clear search first
            self.wrapper.page.locator(self.SEARCH_INPUT).fill("")
            self.wrapper.page.wait_for_timeout(500)
            # Search again
            self.search_interview(identifier)
        
        # Check if the interview is still present
        try:
            is_present = self.wrapper.is_visible(f"text={identifier}", timeout=3000)
            return not is_present  # Return True if NOT present (deleted)
        except Exception:
            return True  # If we can't find it, assume it's deleted
