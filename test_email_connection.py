#!/usr/bin/env python3
"""Test script to verify Gmail IMAP connection and email fetching."""

import sys
from utils.mail_client import GmailIMAPClient, MailClientError
from utils.config_loader import ConfigLoader

def test_gmail_connection():
    """Test Gmail IMAP connection."""
    print("=" * 80)
    print("Gmail IMAP Connection Test")
    print("=" * 80)
    
    # Load configuration
    config_loader = ConfigLoader()
    gmail_email = config_loader.get("gmail_email")
    gmail_app_password = config_loader.get("gmail_app_password")
    
    print(f"\n📧 Email: {gmail_email}")
    print(f"🔑 App Password: {'*' * (len(gmail_app_password) - 4) + gmail_app_password[-4:]}")
    
    if not gmail_email or not gmail_app_password:
        print("\n❌ ERROR: Gmail credentials not configured in .env file")
        return False
    
    try:
        # Connect to Gmail
        print("\n🔄 Connecting to Gmail IMAP server...")
        mail_client = GmailIMAPClient(gmail_email, gmail_app_password)
        mail_client.connect()
        print("✅ Successfully connected to Gmail!")
        
        # Check INBOX
        print("\n📥 Checking INBOX...")
        inbox_messages = mail_client.list_messages(
            folder="INBOX",
            max_results=5,
            search_criteria='ALL'
        )
        print(f"✅ Found {len(inbox_messages)} messages in INBOX")
        for i, msg in enumerate(inbox_messages[:3], 1):
            print(f"   {i}. {msg.subject[:60]}")
        
        # Check for Interview Invitation emails in INBOX
        print("\n🔍 Searching for 'Interview Invitation' in INBOX...")
        interview_emails = mail_client.list_messages(
            folder="INBOX",
            max_results=5,
            search_criteria='SUBJECT "Interview Invitation"'
        )
        print(f"✅ Found {len(interview_emails)} Interview Invitation emails in INBOX")
        for i, msg in enumerate(interview_emails, 1):
            print(f"   {i}. {msg.subject} - {msg.date}")
        
        # Check SPAM folder
        print("\n🗑️  Checking [Gmail]/Spam folder...")
        try:
            spam_messages = mail_client.list_messages(
                folder="[Gmail]/Spam",
                max_results=5,
                search_criteria='ALL'
            )
            print(f"✅ Found {len(spam_messages)} messages in Spam")
            for i, msg in enumerate(spam_messages[:3], 1):
                print(f"   {i}. {msg.subject[:60]}")
            
            # Check for Interview Invitation emails in SPAM
            print("\n🔍 Searching for 'Interview Invitation' in Spam...")
            spam_interview_emails = mail_client.list_messages(
                folder="[Gmail]/Spam",
                max_results=5,
                search_criteria='SUBJECT "Interview Invitation"'
            )
            print(f"✅ Found {len(spam_interview_emails)} Interview Invitation emails in Spam")
            for i, msg in enumerate(spam_interview_emails, 1):
                print(f"   {i}. {msg.subject} - {msg.date}")
                
        except Exception as e:
            print(f"⚠️  Could not check Spam folder: {e}")
        
        # Disconnect
        mail_client.disconnect()
        print("\n✅ Connection test completed successfully!")
        print("=" * 80)
        return True
        
    except MailClientError as e:
        print(f"\n❌ ERROR: Failed to connect to Gmail: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Verify your app password is correct (16 characters, may have spaces)")
        print("   2. Ensure 2FA is enabled on your Google account")
        print("   3. Generate a new app password at: https://myaccount.google.com/apppasswords")
        print("   4. Check that IMAP is enabled in Gmail settings")
        print("=" * 80)
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print("=" * 80)
        return False


if __name__ == "__main__":
    success = test_gmail_connection()
    sys.exit(0 if success else 1)
