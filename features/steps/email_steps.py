from __future__ import annotations

from behave import given, when, then

from core.reporting.allure_manager import AllureManager
from utils.mail_client import GmailIMAPClient, MailClientError


@given("I connect to Gmail inbox")
def step_connect_to_gmail(context):
    """Connect to Gmail using IMAP."""
    email_address = context.config_loader.get("gmail_email")
    app_password = context.config_loader.get("gmail_app_password")
    
    if not email_address or not app_password:
        raise ValueError(
            "Gmail credentials not configured. "
            "Set GMAIL_EMAIL and GMAIL_APP_PASSWORD in .env"
        )
    
    context.mail_client = GmailIMAPClient(email_address, app_password)
    context.mail_client.connect()
    context.logger.info(f"Connected to Gmail: {email_address}")


@when('I fetch the latest "{count:d}" emails')
def step_fetch_emails(context, count: int):
    """Fetch latest emails from inbox."""
    context.emails = context.mail_client.list_messages(max_results=count)
    context.logger.info(f"Fetched {len(context.emails)} emails")


@when('I search for emails with subject "{subject}"')
def step_search_emails_by_subject(context, subject: str):
    """Search for emails with specific subject."""
    context.emails = context.mail_client.search_messages(subject=subject, max_results=10)
    context.logger.info(f"Found {len(context.emails)} emails matching subject: {subject}")


@then("I should see the email list")
def step_verify_email_list(context):
    """Verify emails were retrieved and display them."""
    assert context.emails is not None, "No emails fetched"
    
    email_summary = []
    for i, email in enumerate(context.emails, 1):
        summary = f"\n--- Email {i} ---\n"
        summary += f"Subject: {email.subject}\n"
        summary += f"From: {email.sender}\n"
        summary += f"Date: {email.date}\n"
        summary += f"Preview: {email.snippet[:100]}...\n"
        email_summary.append(summary)
        context.logger.info(summary)
    
    AllureManager.attach_text("Email List", "\n".join(email_summary))
    print("\n" + "="*50)
    print(f"Found {len(context.emails)} emails:")
    print("="*50)
    for summary in email_summary:
        print(summary)


@then("I should see matching emails")
def step_verify_matching_emails(context):
    """Verify matching emails were found."""
    if not context.emails:
        context.logger.info("No matching emails found")
        print("\nNo matching emails found")
        return
    
    email_summary = []
    for i, email in enumerate(context.emails, 1):
        summary = f"\n--- Matching Email {i} ---\n"
        summary += f"Subject: {email.subject}\n"
        summary += f"From: {email.sender}\n"
        summary += f"Date: {email.date}\n"
        summary += f"Preview: {email.snippet[:100]}...\n"
        email_summary.append(summary)
        context.logger.info(summary)
    
    AllureManager.attach_text("Matching Emails", "\n".join(email_summary))
    print("\n" + "="*50)
    print(f"Found {len(context.emails)} matching emails:")
    print("="*50)
    for summary in email_summary:
        print(summary)
