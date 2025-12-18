#!/usr/bin/env python3
"""Check the actual subject and content of interview emails."""

from utils.mail_client import GmailIMAPClient
from utils.config_loader import ConfigLoader

# Load configuration
config_loader = ConfigLoader()
gmail_email = config_loader.get("gmail_email")
gmail_app_password = config_loader.get("gmail_app_password")

print("=" * 80)
print("Checking Interview Email Details")
print("=" * 80)

# Connect to Gmail
mail_client = GmailIMAPClient(gmail_email, gmail_app_password)
mail_client.connect()

# Check Spam folder for interview emails
print("\n🔍 Checking Spam folder for interview-related emails...")
spam_messages = mail_client.list_messages(
    folder="[Gmail]/Spam",
    max_results=10,
    search_criteria='ALL'
)

interview_related = []
for msg in spam_messages:
    if 'interview' in msg.subject.lower() or 'candidate' in msg.subject.lower():
        interview_related.append(msg)

print(f"\n✅ Found {len(interview_related)} interview-related emails:")
for i, msg in enumerate(interview_related, 1):
    print(f"\n{i}. Subject: {msg.subject}")
    print(f"   From: {msg.sender}")
    print(f"   Date: {msg.date}")
    print(f"   Snippet: {msg.snippet[:100]}...")
    
    # Check if there's a URL in the body
    if msg.body:
        import re
        url_pattern = r'https?://[^\s<>"]+/interview/[^\s<>"]+'
        matches = re.findall(url_pattern, msg.body)
        if matches:
            print(f"   URL Found: {matches[0]}")

mail_client.disconnect()
print("\n" + "=" * 80)
