#!/usr/bin/env python3
"""
Quick helper to get an interview link manually.
Just follow the steps and paste the link when you have it.
"""

import os


def main():
    print("=" * 70)
    print("GET INTERVIEW LINK")
    print("=" * 70)
    print("\nPlease follow these steps to get an interview link:\n")
    print("1. Open: https://talenttalks.vlinkinfo.com/login")
    print("2. Login with:")
    print("   - Email: jitender.sachdeva@vlinkinfo.com")
    print("   - Password: Vlink@123")
    print("\n3. Click 'Schedule Interview' in the sidebar")
    print("4. Fill the form:")
    print("   - Select any existing job opening")
    print("   - Candidate Name: Test Candidate")
    print("   - Candidate Email: test@example.com")
    print("   - Interview Date: Today")
    print("   - Interview Time: Current time (or any past/present time)")
    print("\n5. Click 'Schedule Interview' button")
    print("6. Copy the interview link from the modal/success message")
    print("\n" + "=" * 70)
    print("\nPaste the interview link below:")
    interview_link = input().strip()
    
    if not interview_link:
        print("❌ No link provided. Exiting.")
        return
    
    if "talenttalks" not in interview_link or "interview" not in interview_link:
        print("⚠️  WARNING: This doesn't look like a valid interview link")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            return
    
    # Export to environment
    print(f"\n✅ Interview link received: {interview_link}\n")
    print("To run the test, execute:")
    print(f"export INTERVIEW_LINK='{interview_link}'")
    print("python -m behave features/test_tts_cdp.feature --no-capture")
    print("\nOr run both commands together:")
    print(f"INTERVIEW_LINK='{interview_link}' python -m behave features/test_tts_cdp.feature --no-capture")


if __name__ == "__main__":
    main()
