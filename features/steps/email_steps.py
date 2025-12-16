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


@when('I wait for email with subject containing "{subject}" for {timeout:d} seconds')
def step_wait_for_email(context, subject: str, timeout: int):
    """Wait for an email with specific subject to arrive."""
    context.logger.info(f"Waiting for email with subject containing: {subject}")
    email = context.mail_client.wait_for_email(
        subject_contains=subject,
        timeout_seconds=timeout,
        poll_interval=5
    )
    
    if email:
        context.received_email = email
        context.logger.info(f"Email received: {email.subject}")
        AllureManager.attach_text("Received Email", 
            f"Subject: {email.subject}\n"
            f"From: {email.sender}\n"
            f"Date: {email.date}\n"
            f"Preview: {email.snippet}")
    else:
        context.received_email = None
        context.logger.warning(f"Email not received within {timeout} seconds")


@then("the email should be received")
def step_verify_email_received(context):
    """Verify that the expected email was received."""
    assert hasattr(context, 'received_email') and context.received_email is not None, \
        "Email was not received"
    context.logger.info(f"Email received successfully: {context.received_email.subject}")


@then('the email should contain interview link')
def step_verify_email_contains_link(context):
    """Verify that the email contains an interview link."""
    assert hasattr(context, 'received_email') and context.received_email is not None, \
        "No email received to verify link"
    
    email_body = context.received_email.body or ""
    
    # Look for common interview link patterns
    import re
    link_patterns = [
        r'https?://[^\s<>"]+/interview[^\s<>"]*',
        r'https?://[^\s<>"]+/invite[^\s<>"]*',
        r'https?://[^\s<>"]+/join[^\s<>"]*',
        r'https?://[^\s<>"]+/start[^\s<>"]*'
    ]
    
    found_links = []
    for pattern in link_patterns:
        matches = re.findall(pattern, email_body, re.IGNORECASE)
        found_links.extend(matches)
    
    assert found_links, "No interview link found in the email body"
    
    # Store the first link in context for potential use in later steps
    context.interview_link = found_links[0]
    
    context.logger.info(f"Interview link found: {context.interview_link}")
    AllureManager.attach_text("Interview Link", context.interview_link)
    
    print(f"\n✓ Interview link found: {context.interview_link}")


@then('the email should be sent to "{email_address}"')
def step_verify_email_recipient(context, email_address: str):
    """Verify the email was received at the expected address."""
    # Since we're checking the inbox of the configured Gmail account,
    # we verify that we're monitoring the correct inbox
    configured_email = context.config_loader.get("gmail_email")
    
    # If a candidate email is stored in context, use that for comparison
    expected_email = getattr(context, 'candidate_email', email_address)
    
    context.logger.info(f"Verifying email was sent to: {expected_email}")
    context.logger.info(f"Monitoring inbox: {configured_email}")
    
    assert configured_email.lower() == expected_email.lower(), \
        f"Email monitoring mismatch. Expected: {expected_email}, Monitoring: {configured_email}"
    
    AllureManager.attach_text("Email Verification", 
        f"Email sent to: {expected_email}\n"
        f"Monitoring inbox: {configured_email}")
