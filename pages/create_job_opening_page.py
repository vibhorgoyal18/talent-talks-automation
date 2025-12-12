from __future__ import annotations

from typing import List, Optional

from core.web.playwright_wrapper import PlaywrightWrapper


class CreateJobOpeningPage:
    """Page Object for the Create Job Opening page."""

    PATH = "/templates/new"

    # Page header
    PAGE_HEADING = "role=heading[name='Create New Job Opening']"
    BACK_LINK = "role=link[name='Back to Job Openings']"

    # Job Opening Details
    JOB_NAME_INPUT = "role=textbox[name='Job Opening Name']"
    JOB_DESCRIPTION_INPUT = "role=textbox[name='Enter or paste job description']"
    GENERATE_SKILLS_BUTTON = "role=button[name='Generate Skills']"

    # Interview Settings
    INTERVIEW_DURATION_INPUT = "role=spinbutton[name='Interview Duration (minutes)']"

    # Evaluation Settings
    ENABLE_RESUME_EVALUATION_CHECKBOX = "role=checkbox[name='Enable Resume Evaluation']"
    RESUME_EVALUATION_PERCENTAGE_INPUT = "role=spinbutton[name='Resume Evaluation Percentage']"
    ENABLE_STATIC_QUESTIONS_CHECKBOX = "role=checkbox[name='Enable Static Questions']"
    ENABLE_CODE_EVALUATION_CHECKBOX = "role=checkbox[name='Enable Code Evaluation']"
    PROGRAMMING_LANGUAGE_COMBOBOX = "role=combobox[name='Programming Language']"

    # Tech Stack
    ADD_TECHNOLOGY_INPUT = "role=textbox[name='Add Technology']"
    ADD_TECH_BUTTON = "role=button[name='Add']"
    EDIT_TECH_STACK_BUTTON = "role=button[name='Edit Tech Stack']"

    # Actions
    CANCEL_BUTTON = "role=button[name='Cancel']"
    CREATE_JOB_BUTTON = "role=button[name='Create Job Opening']"

    # Success/Error messages
    SUCCESS_MESSAGE = "[role='alert']"

    def __init__(self, wrapper: PlaywrightWrapper, base_url: str) -> None:
        self.wrapper = wrapper
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        """Navigate directly to the create job opening page."""
        self.wrapper.go_to(f"{self.base_url}{self.PATH}")

    def is_loaded(self) -> bool:
        """Check if the page is loaded."""
        return self.wrapper.is_visible(self.PAGE_HEADING, timeout=5000)

    def wait_for_page_load(self) -> None:
        """Wait for the page to be fully loaded."""
        self.wrapper.wait_for_selector(self.JOB_NAME_INPUT, state="visible")

    def enter_job_name(self, name: str) -> None:
        """Enter job opening name."""
        self.wrapper.type_text(self.JOB_NAME_INPUT, name)

    def enter_job_description(self, description: str) -> None:
        """Enter job description."""
        self.wrapper.type_text(self.JOB_DESCRIPTION_INPUT, description)

    def set_interview_duration(self, minutes: int) -> None:
        """Set interview duration in minutes."""
        self.wrapper.type_text(self.INTERVIEW_DURATION_INPUT, str(minutes))

    def enable_resume_evaluation(self, percentage: int = 10) -> None:
        """Enable resume evaluation and set percentage."""
        checkbox = self.wrapper.locator(self.ENABLE_RESUME_EVALUATION_CHECKBOX)
        if not checkbox.is_checked():
            self.wrapper.click(self.ENABLE_RESUME_EVALUATION_CHECKBOX)
        # Wait for percentage field to appear and set value
        self.wrapper.wait_for_selector(self.RESUME_EVALUATION_PERCENTAGE_INPUT, state="visible")
        self.wrapper.type_text(self.RESUME_EVALUATION_PERCENTAGE_INPUT, str(percentage))

    def disable_resume_evaluation(self) -> None:
        """Disable resume evaluation if enabled."""
        checkbox = self.wrapper.locator(self.ENABLE_RESUME_EVALUATION_CHECKBOX)
        if checkbox.is_checked():
            self.wrapper.click(self.ENABLE_RESUME_EVALUATION_CHECKBOX)

    def enable_static_questions(self) -> None:
        """Enable static questions."""
        checkbox = self.wrapper.locator(self.ENABLE_STATIC_QUESTIONS_CHECKBOX)
        if not checkbox.is_checked():
            self.wrapper.click(self.ENABLE_STATIC_QUESTIONS_CHECKBOX)

    def enable_code_evaluation(self, language: str) -> None:
        """Enable code evaluation and select programming language."""
        checkbox = self.wrapper.locator(self.ENABLE_CODE_EVALUATION_CHECKBOX)
        if not checkbox.is_checked():
            self.wrapper.click(self.ENABLE_CODE_EVALUATION_CHECKBOX)
        # Wait for language dropdown and select
        self.wrapper.wait_for_selector(self.PROGRAMMING_LANGUAGE_COMBOBOX, state="visible")
        self.wrapper.click(self.PROGRAMMING_LANGUAGE_COMBOBOX)
        # Select the language from dropdown
        language_option = f"role=option[name='{language}']"
        self.wrapper.click(language_option)

    def disable_code_evaluation(self) -> None:
        """Disable code evaluation if enabled."""
        checkbox = self.wrapper.locator(self.ENABLE_CODE_EVALUATION_CHECKBOX)
        if checkbox.is_checked():
            self.wrapper.click(self.ENABLE_CODE_EVALUATION_CHECKBOX)

    def add_technology(self, tech: str) -> None:
        """Add a technology to the tech stack."""
        self.wrapper.type_text(self.ADD_TECHNOLOGY_INPUT, tech)
        self.wrapper.click(self.ADD_TECH_BUTTON)

    def add_technologies(self, tech_list: List[str]) -> None:
        """Add multiple technologies to the tech stack."""
        for tech in tech_list:
            self.add_technology(tech)

    def click_generate_skills(self) -> None:
        """Click the Generate Skills button."""
        self.wrapper.click(self.GENERATE_SKILLS_BUTTON)

    def click_cancel(self) -> None:
        """Click cancel button."""
        self.wrapper.click(self.CANCEL_BUTTON)

    def click_create_job_opening(self) -> None:
        """Click the Create Job Opening button."""
        self.wrapper.click(self.CREATE_JOB_BUTTON)

    def is_create_button_enabled(self) -> bool:
        """Check if the Create Job Opening button is enabled."""
        return self.wrapper.is_enabled(self.CREATE_JOB_BUTTON)

    def is_success_message_displayed(self) -> bool:
        """Check if success message is displayed."""
        return self.wrapper.is_visible(self.SUCCESS_MESSAGE, timeout=5000)

    def get_success_message(self) -> str:
        """Get the success message text."""
        return self.wrapper.get_text(self.SUCCESS_MESSAGE)

    def create_job_opening(
        self,
        job_name: str,
        job_description: str,
        interview_duration: int,
        enable_resume_evaluation: bool = False,
        resume_evaluation_percentage: int = 0,
        enable_code_evaluation: bool = False,
        programming_language: Optional[str] = None,
        tech_stack: Optional[List[str]] = None,
    ) -> None:
        """Fill in all job opening details and create the job.
        
        Args:
            job_name: Name of the job opening
            job_description: Description of the job
            interview_duration: Duration in minutes
            enable_resume_evaluation: Whether to enable resume evaluation
            resume_evaluation_percentage: Percentage for resume evaluation (if enabled)
            enable_code_evaluation: Whether to enable code evaluation
            programming_language: Programming language for code evaluation
            tech_stack: List of technologies to add
        """
        self.wait_for_page_load()
        
        # Fill basic details
        self.enter_job_name(job_name)
        self.enter_job_description(job_description)
        self.set_interview_duration(interview_duration)
        
        # Configure evaluation settings
        if enable_resume_evaluation:
            self.enable_resume_evaluation(resume_evaluation_percentage)
        
        if enable_code_evaluation and programming_language:
            self.enable_code_evaluation(programming_language)
        
        # Add tech stack
        if tech_stack:
            self.add_technologies(tech_stack)
        
        # Click create button
        self.click_create_job_opening()
