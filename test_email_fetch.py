#!/usr/bin/env python3
"""Test the updated email fetching logic."""

import time
from utils.mail_client import GmailIMAPClient
from utils.config_loader import ConfigLoader

# Load configuration
config_loader = ConfigLoader()
gmail_email = config_loader.get("gmail_email")
gmail_app_password = config_loader.get("gmail_app_password")

print("=" * 80)
print("Testing Interview Email Fetching (Updated Logic)")
print("=" * 80)

# Connect to Gmail
mail_client = GmailIMAPClient(gmail_email, gmail_app_password)
mail_client.connect()

print(f"\n📧 Checking email: {gmail_email}")

email_message = None
folder_found = None

# Try INBOX first, then Spam folder
folders_to_check = [("INBOX", "📥 Inbox"), ("[Gmail]/Spam", "🗑️ Spam")]

timeout_seconds = 15  # Shorter timeout for testing
poll_interval = 3
start_time = time.time()

while time.time() - start_time < timeout_seconds:
    for folder, folder_display in folders_to_check:
        try:
            # Search for "Interview Link" which is the actual subject prefix
            messages = mail_client.list_messages(
                folder=folder,
                max_results=5,
                search_criteria='SUBJECT "Interview Link"'
            )
            
            if messages:
                # Find the most recent matching email
                for msg in messages:
                    if "Interview Link" in msg.subject:
                        email_message = msg
                        folder_found = folder_display
                        break
            
            if email_message:
                break
        except Exception as e:
            print(f"⚠️  Could not check {folder}: {e}")
    
    if email_message:
        break
    
    print(f"⏳ Waiting for email... ({int(time.time() - start_time)}s elapsed)")
    time.sleep(poll_interval)

if email_message:
    print(f"\n✅ Email found in {folder_found}")
    print(f"   Subject: {email_message.subject}")
    print(f"   From: {email_message.sender}")
    print(f"   Date: {email_message.date}")
    
    # Extract URL
    import re
    url_pattern = r'https?://[^\s<>"]+/interview[^\s<>"]*'
    matches = re.findall(url_pattern, email_message.body) if email_message.body else []
    
    if matches:
        interview_url = matches[0]
        print(f"\n{'='*80}")
        print(f"🔗 INTERVIEW INVITATION LINK")
        print(f"{'='*80}")
        print(f"   Found in: {folder_found}")
        print(f"   Link: {interview_url}")
        print(f"{'='*80}")
    else:
        print("\n⚠️  No interview URL found in email body")
else:
    print(f"\n❌ Email not found within {timeout_seconds} seconds")

mail_client.disconnect()
print("\n" + "=" * 80)
