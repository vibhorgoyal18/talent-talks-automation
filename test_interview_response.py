"""Test TTS + CDP integration for sending candidate responses in interview."""

import os
import sys
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from utils.ai.tts import GeminiTTS
from pages.interview_page import InterviewPage
from core.web.playwright_wrapper import PlaywrightWrapper

# Load environment
load_dotenv()

def test_interview_response():
    """Test sending candidate response using TTS + CDP in an active interview."""
    
    # You need to manually provide an interview link
    # Get one from: https://talenttalks.vlinkinfo.com/dashboard
    interview_link = input("\nEnter interview link: ").strip()
    
    if not interview_link:
        print("❌ No interview link provided")
        return False
    
    print("=" * 60)
    print("Testing TTS + CDP Integration for Interview Response")
    print("=" * 60)
    
    with sync_playwright() as p:
        # Launch browser in headed mode to see what happens
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500,
            args=[
                "--use-fake-device-for-media-stream",
                "--use-fake-ui-for-media-stream",
                "--auto-select-desktop-capture-source=Screen"
            ]
        )
        
        context = browser.new_context(
            permissions=["microphone", "camera"],
            viewport={"width": 1280, "height": 720}
        )
        
        page = context.new_page()
        
        try:
            # Create wrapper and interview page
            wrapper = PlaywrightWrapper(page)
            interview_page = InterviewPage(wrapper, "https://talenttalks.vlinkinfo.com")
            
            print("\n1. Navigating to interview...")
            page.goto(interview_link)
            page.wait_for_load_state("networkidle")
            print("✅ Interview page loaded")
            
            print("\n2. Waiting for interview to be ready...")
            page.wait_for_timeout(3000)
            
            # Check if we need to start the interview
            try:
                start_button = page.locator(interview_page.START_INTERVIEW_BUTTON).first
                if start_button.is_visible(timeout=2000):
                    print("   Found Start Interview button, clicking...")
                    start_button.click()
                    page.wait_for_timeout(5000)
                    print("✅ Interview started")
            except:
                print("   Interview already started or button not found")
            
            print("\n3. Opening transcript panel...")
            try:
                show_transcript_btn = page.locator(interview_page.SHOW_TRANSCRIPTS_BUTTON).first
                if show_transcript_btn.is_visible(timeout=3000):
                    show_transcript_btn.click()
                    page.wait_for_timeout(2000)
                    print("✅ Transcript panel opened")
                else:
                    print("⚠️  Transcript button not found")
            except Exception as e:
                print(f"⚠️  Could not open transcript: {e}")
            
            print("\n4. Reading current transcript...")
            transcript_lines = interview_page.get_transcript_content()
            print(f"   Found {len(transcript_lines)} transcript entries:")
            for line in transcript_lines[:3]:
                print(f"   - {line[:80]}...")
            
            print("\n5. Initializing TTS with Gemini...")
            tts = GeminiTTS()
            if not tts.enabled:
                print("❌ TTS not enabled. Check GEMINI_API_KEY")
                return False
            print("✅ TTS initialized")
            
            print("\n6. Preparing candidate response...")
            original_text = "I am doing great, thank you for asking. I have five years of Python development experience."
            
            # Process with Gemini TTS
            processed_text = tts.generate_speech(original_text)
            print(f"   Original: {original_text}")
            print(f"   Processed: {processed_text[:150]}...")
            
            print("\n7. Sending response via CDP injection...")
            interview_page.send_candidate_response(processed_text)
            
            print("\n8. Waiting for response to appear in transcript...")
            page.wait_for_timeout(5000)
            
            print("\n9. Reading updated transcript...")
            updated_transcript = interview_page.get_transcript_content()
            print(f"   Found {len(updated_transcript)} transcript entries:")
            for line in updated_transcript[-5:]:
                print(f"   - {line[:100]}...")
            
            # Check if our response appears
            response_found = any("Candidate:" in line for line in updated_transcript)
            
            if response_found:
                print("\n✅ SUCCESS: Candidate response found in transcript!")
            else:
                print("\n⚠️  Candidate response not found in transcript")
                print("   This might mean CDP injection didn't work with this interview instance")
            
            print("\n10. Keeping browser open for 30 seconds for manual inspection...")
            page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_interview_response()
    sys.exit(0 if success else 1)
