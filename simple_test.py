"""
Simple standalone test for TTS + CDP integration.
Just paste an interview link when prompted and it will test the integration.
"""

import asyncio
from playwright.async_api import async_playwright
from utils.ai.tts import GeminiTTS
import os
from dotenv import load_dotenv

load_dotenv()


async def test_tts_cdp_injection(interview_url: str):
    """Test TTS processing and CDP injection with a given interview URL."""
    
    # Initialize TTS
    print("🔧 Initializing Gemini TTS...")
    tts = GeminiTTS()
    
    # Candidate response to test
    candidate_text = "I am doing great, thank you for asking. I have five years of Python development experience."
    print(f"\n📝 Original text: {candidate_text}")
    
    # Process with TTS
    print("🤖 Processing with Gemini TTS...")
    processed_text = tts.generate_speech(candidate_text)
    print(f"✨ Processed text: {processed_text}")
    
    # Open browser and inject
    print("\n🌐 Opening browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print(f"🔗 Navigating to: {interview_url}")
        await page.goto(interview_url, wait_until="domcontentloaded", timeout=60000)
        
        # Wait for interview to load
        print("⏳ Waiting for interview to load...")
        await asyncio.sleep(3)
        
        # Check if we need to start the interview
        try:
            start_button = page.locator("button:has-text('Start Interview')")
            if await start_button.is_visible(timeout=2000):
                print("▶️ Starting interview...")
                await start_button.click()
                await asyncio.sleep(2)
        except:
            print("ℹ️ Interview already started or Start button not found")
        
        # Open transcript
        print("📋 Opening transcript...")
        try:
            transcript_button = page.locator("button:has-text('Show Transcripts')")
            if await transcript_button.is_visible(timeout=2000):
                await transcript_button.click()
                await asyncio.sleep(1)
            else:
                # Try alternate selector
                transcript_button = page.locator("button.show-transcripts-btn")
                if await transcript_button.is_visible(timeout=2000):
                    await transcript_button.click()
                    await asyncio.sleep(1)
        except Exception as e:
            print(f"⚠️ Could not open transcript: {e}")
        
        # Read current transcript
        print("📖 Reading current transcript...")
        try:
            transcript_panel = page.locator(".transcript-panel, .transcript-content, [class*='transcript']")
            if await transcript_panel.is_visible(timeout=2000):
                current_transcript = await transcript_panel.text_content()
                print(f"Current transcript:\n{current_transcript[:200]}...")
        except:
            print("⚠️ Could not read transcript yet")
        
        # Inject candidate response using CDP
        print(f"\n💉 Injecting candidate response via CDP...")
        print(f"   Text to inject: {processed_text}")
        
        try:
            cdp = await context.new_cdp_session(page)
            
            # Create JavaScript expression to inject speech result
            js_expression = f"""
            (function() {{
                try {{
                    // Find SpeechRecognition instance
                    let recognition = null;
                    
                    // Try to find it in window
                    if (window.recognition) {{
                        recognition = window.recognition;
                    }} else {{
                        // Search in all window properties
                        for (let key in window) {{
                            if (window[key] && 
                                typeof window[key] === 'object' && 
                                window[key].constructor.name.includes('SpeechRecognition')) {{
                                recognition = window[key];
                                break;
                            }}
                        }}
                    }}
                    
                    if (recognition && recognition.onresult) {{
                        // Create fake speech result
                        const responseText = {repr(processed_text)};
                        const fakeEvent = {{
                            results: [[{{
                                transcript: responseText,
                                confidence: 0.95,
                                isFinal: true
                            }}]],
                            resultIndex: 0
                        }};
                        
                        // Trigger the onresult handler
                        recognition.onresult(fakeEvent);
                        return 'SUCCESS: Injected speech result';
                    }} else {{
                        return 'ERROR: SpeechRecognition instance not found or onresult not set';
                    }}
                }} catch (err) {{
                    return 'ERROR: ' + err.message;
                }}
            }})();
            """
            
            result = await cdp.send("Runtime.evaluate", {
                "expression": js_expression,
                "returnByValue": True
            })
            
            injection_result = result.get("result", {}).get("value", "Unknown")
            print(f"   CDP Result: {injection_result}")
            
        except Exception as e:
            print(f"❌ CDP injection failed: {e}")
        
        # Wait and check transcript again
        print("\n⏳ Waiting 3 seconds for transcript update...")
        await asyncio.sleep(3)
        
        # Verify in transcript
        print("🔍 Checking if response appears in transcript...")
        try:
            transcript_panel = page.locator(".transcript-panel, .transcript-content, [class*='transcript']")
            if await transcript_panel.is_visible(timeout=2000):
                updated_transcript = await transcript_panel.text_content()
                print(f"\nUpdated transcript:\n{updated_transcript}")
                
                if processed_text in updated_transcript or candidate_text in updated_transcript:
                    print("\n✅ SUCCESS: Candidate response found in transcript!")
                else:
                    print("\n⚠️ WARNING: Candidate response NOT found in transcript")
                    print("   This might mean CDP injection didn't work or transcript hasn't updated yet")
            else:
                print("⚠️ Could not read updated transcript")
        except Exception as e:
            print(f"❌ Error reading transcript: {e}")
        
        # Keep browser open
        print("\n👁️ Keeping browser open for 30 seconds for manual inspection...")
        print("   Check the interview page to see if the response appeared!")
        await asyncio.sleep(30)
        
        print("🏁 Test complete. Closing browser...")
        await browser.close()


def main():
    """Main entry point."""
    print("=" * 70)
    print("TTS + CDP Integration Test")
    print("=" * 70)
    
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ ERROR: GEMINI_API_KEY not found in .env file")
        return
    
    # Get interview URL from user
    print("\n📝 Please paste the interview URL below:")
    print("   (Example: https://talenttalks.vlinkinfo.com/interview?name=...&interviewId=...)")
    interview_url = input("\nInterview URL: ").strip()
    
    if not interview_url:
        print("❌ No URL provided. Exiting.")
        return
    
    if "talenttalks" not in interview_url or "interview" not in interview_url:
        print("⚠️ WARNING: URL doesn't look like a valid interview link")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            return
    
    # Run the test
    print(f"\n🚀 Starting test with URL: {interview_url}\n")
    asyncio.run(test_tts_cdp_injection(interview_url))
    
    print("\n✨ All done!")


if __name__ == "__main__":
    main()
