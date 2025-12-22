"""Quick test to verify TTS + CDP integration for candidate response simulation."""

import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from utils.ai.tts import GeminiTTS
from core.web.playwright_wrapper import PlaywrightWrapper
from pages.interview_page import InterviewPage

load_dotenv()

# Use a recent interview link (you'll need to update this)
INTERVIEW_LINK = "https://talenttalks.vlinkinfo.com/interview?name=Python_1222_1544&interviewId=69490658cb423cc8fe89df0f"

def test_tts_cdp_integration():
    """Test TTS text processing with CDP injection."""
    print("=" * 70)
    print("Testing TTS + CDP Integration for Candidate Response Simulation")
    print("=" * 70)
    
    # Initialize TTS
    print("\n1. Initializing Gemini TTS...")
    tts = GeminiTTS()
    
    if not tts.enabled:
        print("❌ TTS not enabled. Check GEMINI_API_KEY in .env")
        return False
    
    print(f"✅ TTS initialized")
    
    # Process candidate response text
    print("\n2. Processing candidate response with Gemini LLM...")
    original_text = "I am doing great, thank you for asking. I have five years of Python development experience."
    
    processed_text = tts.generate_speech(original_text)
    print(f"✅ Text processed by Gemini:")
    print(f"   Original: {original_text}")
    print(f"   Processed: {processed_text[:200]}...")
    
    # Launch browser and navigate to interview
    print(f"\n3. Opening interview link...")
    print(f"   URL: {INTERVIEW_LINK}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()
        
        # Grant permissions
        context.grant_permissions(['microphone', 'camera'])
        
        page = context.new_page()
        wrapper = PlaywrightWrapper(page)
        
        # Navigate to interview
        page.goto(INTERVIEW_LINK)
        page.wait_for_timeout(3000)
        
        interview_page = InterviewPage(wrapper, "https://talenttalks.vlinkinfo.com")
        
        print("✅ Interview page loaded")
        
        # Start interview if needed
        print("\n4. Starting interview...")
        try:
            if interview_page.is_start_button_visible():
                interview_page.click_start_interview()
                print("✅ Clicked Start Interview button")
                page.wait_for_timeout(5000)
            else:
                print("ℹ️  Interview already started")
        except Exception as e:
            print(f"⚠️  Could not start interview: {e}")
        
        # Open transcript
        print("\n5. Opening transcript panel...")
        try:
            interview_page.click_show_transcripts()
            page.wait_for_timeout(2000)
            
            if interview_page.is_transcript_panel_visible():
                print("✅ Transcript panel opened")
                
                # Read current transcript
                transcript = interview_page.get_transcript_content()
                print(f"   Current transcript ({len(transcript)} lines):")
                for line in transcript[:3]:
                    print(f"     - {line[:80]}...")
            else:
                print("⚠️  Transcript panel not visible")
        except Exception as e:
            print(f"❌ Error opening transcript: {e}")
        
        # Send candidate response using CDP + processed text
        print("\n6. Sending candidate response via CDP + TTS...")
        print(f"   Using processed text from Gemini")
        
        try:
            # Extract a concise version from the processed text
            # (Gemini returns multiple options, we'll use the first one)
            if "**Option 1" in processed_text:
                # Extract the first option
                lines = processed_text.split('\n')
                response_text = None
                for i, line in enumerate(lines):
                    if "**Option 1" in line and i + 1 < len(lines):
                        response_text = lines[i + 1].strip().strip('"')
                        break
                
                if not response_text:
                    response_text = original_text
            else:
                response_text = processed_text[:150]  # Use first 150 chars
            
            print(f"   Sending: {response_text}")
            interview_page.send_candidate_response(response_text)
            print("✅ Candidate response sent via CDP")
            
            # Wait and re-read transcript
            page.wait_for_timeout(3000)
            
            new_transcript = interview_page.get_transcript_content()
            print(f"\n7. Verifying response in transcript...")
            print(f"   Transcript now has {len(new_transcript)} lines")
            
            # Check if our response appears
            found = False
            for line in new_transcript:
                if response_text[:30] in line or "Candidate:" in line:
                    print(f"   ✅ Found in transcript: {line[:100]}...")
                    found = True
                    break
            
            if not found:
                print("   ⚠️  Response not found in transcript (may need different approach)")
                print("   Latest transcript:")
                for line in new_transcript[-5:]:
                    print(f"     - {line[:100]}...")
            
        except Exception as e:
            print(f"❌ Error sending response: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n8. Keeping browser open for manual inspection...")
        print("   Press Ctrl+C to close")
        
        try:
            page.wait_for_timeout(60000)  # Wait 60 seconds
        except KeyboardInterrupt:
            print("\n   Closing browser...")
        
        browser.close()
    
    print("\n" + "=" * 70)
    print("Test completed")
    print("=" * 70)
    return True

if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Update INTERVIEW_LINK variable with a valid interview link!")
    print("You can get one from the full test run or create manually.\n")
    
    input("Press Enter to continue...")
    test_tts_cdp_integration()
