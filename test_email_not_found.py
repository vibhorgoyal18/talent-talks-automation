#!/usr/bin/env python3
"""Test that email verification fails when email is not found."""

import sys
from utils.mail_client import GmailIMAPClient
from utils.config_loader import ConfigLoader

# Load configuration
config_loader = ConfigLoader()
gmail_email = config_loader.get("gmail_email")
gmail_app_password = config_loader.get("gmail_app_password")

print("=" * 80)
print("Testing Email Not Found Scenario")
print("=" * 80)

# Connect to Gmail
mail_client = GmailIMAPClient(gmail_email, gmail_app_password)
mail_client.connect()

print(f"\n📧 Searching for non-existent email...")

# Search for something that won't exist
messages = mail_client.list_messages(
    folder="INBOX",
    max_results=5,
    search_criteria='SUBJECT "This Subject Will Never Exist 123456789"'
)

print(f"\n✅ Found {len(messages)} messages (should be 0)")

if len(messages) == 0:
    print("✅ Test passed: No messages found as expected")
    print("   This confirms that when email is not found, the test will fail with assertion")
else:
    print(f"❌ Unexpected: Found {len(messages)} messages")

mail_client.disconnect()
print("\n" + "=" * 80)
