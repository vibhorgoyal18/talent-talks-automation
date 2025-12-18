"""Step definitions for email-only testing."""

from behave import given, when, then
from utils.mail_client import GmailIMAPClient
from features.steps.step_context import StepContext
import re
import time


@given("I have Gmail credentials configured")
def step_check_gmail_creds(context):
    """Check Gmail credentials are configured."""
    ctx = StepContext(context)
    
    gmail_email = ctx.config.get("gmail_email")
    gmail_app_password = ctx.config.get("gmail_app_password")
    
    assert gmail_email, "Gmail email not configured"
    assert gmail_app_password, "Gmail app password not configured"
    
    context.gmail_email = gmail_email
    context.gmail_app_password = gmail_app_password
    
    print(f"\n✅ Gmail credentials configured: {gmail_email}")


@when("I search for the latest interview invitation email")
def step_search_interview_email(context):
    """Search for interview invitation email in inbox and spam."""
    ctx = StepContext(context)
    
    mail_client = GmailIMAPClient(context.gmail_email, context.gmail_app_password)
    mail_client.connect()
    
    print(f"\n📧 Checking email: {context.gmail_email}")
    
    email_message = None
    folder_found = None
    
    # Check both INBOX and Spam
    folders_to_check = [("INBOX", "📥 Inbox"), ("[Gmail]/Spam", "🗑️ Spam")]
    
    for folder, folder_display in folders_to_check:
        try:
            messages = mail_client.list_messages(
                folder=folder,
                max_results=5,
                search_criteria='SUBJECT "Interview Link"'
            )
            
            if messages:
                for msg in messages:
                    if "Interview Link" in msg.subject:
                        email_message = msg
                        folder_found = folder_display
                        break
            
            if email_message:
                break
        except Exception as e:
            ctx.logger.debug(f"Could not check {folder}: {e}")
    
    context.email_message = email_message
    context.folder_found = folder_found
    mail_client.disconnect()


@then("I should find the email in inbox or spam")
def step_verify_email_found(context):
    """Verify email was found."""
    assert context.email_message is not None, "No interview email found"
    assert context.folder_found is not None, "Email folder not identified"
    
    print(f"\n✅ Email found in {context.folder_found}")
    print(f"   Subject: {context.email_message.subject}")
    print(f"   From: {context.email_message.sender}")
    print(f"   Date: {context.email_message.date}")


@then("I should be able to extract the interview URL")
def step_extract_url(context):
    """Extract interview URL from email."""
    email_message = context.email_message
    folder_found = context.folder_found
    
    assert email_message.body, "Email body is empty"
    
    # Extract URL
    url_pattern = r'https?://[^\s<>"]+/interview[^\s<>"]*'
    matches = re.findall(url_pattern, email_message.body)
    
    assert matches, f"No interview URL found in email body ({len(email_message.body)} chars)"
    
    interview_url = matches[0]
    
    print(f"\n{'='*80}")
    print(f"🔗 INTERVIEW INVITATION LINK")
    print(f"{'='*80}")
    print(f"   Found in: {folder_found}")
    print(f"   Link: {interview_url}")
    print(f"{'='*80}\n")
