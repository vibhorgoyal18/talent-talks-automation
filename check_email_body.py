#!/usr/bin/env python3
"""Check the actual email body content."""

from utils.mail_client import GmailIMAPClient
from utils.config_loader import ConfigLoader

# Load configuration
config_loader = ConfigLoader()
gmail_email = config_loader.get("gmail_email")
gmail_app_password = config_loader.get("gmail_app_password")

print("=" * 80)
print("Checking Email Body Content")
print("=" * 80)

# Connect to Gmail
mail_client = GmailIMAPClient(gmail_email, gmail_app_password)
mail_client.connect()

# Get the latest interview email from Spam
messages = mail_client.list_messages(
    folder="[Gmail]/Spam",
    max_results=1,
    search_criteria='SUBJECT "Interview Link"'
)

if messages:
    msg = messages[0]
    print(f"\n✅ Email found:")
    print(f"   Subject: {msg.subject}")
    print(f"   From: {msg.sender}")
    print(f"   Date: {msg.date}")
    
    print(f"\n📄 Email Body ({len(msg.body) if msg.body else 0} characters):")
    print("=" * 80)
    if msg.body:
        print(msg.body)
    else:
        print("(Empty body)")
    print("=" * 80)
    
    # Try to extract URLs of any kind
    import re
    all_urls = re.findall(r'https?://[^\s<>"]+', msg.body) if msg.body else []
    print(f"\n🔗 All URLs found in email ({len(all_urls)}):")
    for url in all_urls:
        print(f"   - {url}")
else:
    print("\n❌ No interview emails found")

mail_client.disconnect()
