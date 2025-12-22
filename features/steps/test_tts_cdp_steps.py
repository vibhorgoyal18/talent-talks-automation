"""
Step definitions for TTS + CDP integration testing.
"""

import os
from behave import given
from features.steps.step_context import StepContext


@given("I have an active interview link")
def step_have_active_interview_link(context):
    """Ensure an interview link is available in environment or context."""
    ctx = StepContext(context)
    
    # Check if interview link is in environment variable
    interview_link = os.getenv("INTERVIEW_LINK")
    
    if not interview_link:
        # Check if it was set in a previous step (from the full E2E flow)
        interview_link = getattr(context, 'interview_link', None)
    
    if not interview_link:
        raise ValueError(
            "No interview link provided. Set INTERVIEW_LINK environment variable:\n"
            "export INTERVIEW_LINK='https://talenttalks.vlinkinfo.com/interview?name=...&interviewId=...'"
        )
    
    # Store in context for other steps to use
    context.interview_link = interview_link
    ctx.logger.info(f"Using interview link: {interview_link}")
