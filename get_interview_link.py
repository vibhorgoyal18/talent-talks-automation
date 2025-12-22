"""Quick script to fetch the latest interview link from Gmail."""

from utils.mail_client import GmailIMAPClient
from utils.config_loader import ConfigLoader
import re

config = ConfigLoader()
mail_client = GmailIMAPClient(
    email_address=config.get("gmail_email"),
    app_password=config.get("gmail_app_password")
)

print("Fetching latest interview invitation from Gmail...")

# Search for interview invitations
messages = mail_client.search_messages(subject="Interview Invitation", max_results=5)

if messages:
    latest = messages[0]  # Already sorted by date (newest first)
    print(f"\n✅ Found interview invitation:")
    print(f"   Subject: {latest.subject}")
    print(f"   From: {latest.sender}")
    print(f"   Date: {latest.date}")
    
    # Extract interview link from body
    if latest.body:
        import re
        link_match = re.search(r'https://talenttalks\.vlinkinfo\.com/interview\?[^\s<>"]+', latest.body)
        if link_match:
            interview_link = link_match.group(0)
            print(f"   Interview Link: {interview_link}")
            print(f"\n✅ Update test_tts_cdp.py with this link:")
            print(f'INTERVIEW_LINK = "{interview_link}"')
        else:
            print("\n❌ Could not extract interview link from email body")
            print("Email snippet:", latest.snippet)
    else:
        print("\n❌ Email body is empty")
else:
    print("\n❌ No recent interview invitation found")
    print("You may need to:")
    print("1. Create a new interview manually from the dashboard")
    print("2. Or wait for the email to arrive")

mail_client.disconnect()
