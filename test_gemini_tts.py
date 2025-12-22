#!/usr/bin/env python3
"""
Quick test to verify Gemini TTS is working correctly.
This doesn't require an interview link - just tests the TTS processing.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_tts():
    """Test Gemini TTS processing."""
    print("=" * 70)
    print("GEMINI TTS TEST")
    print("=" * 70)
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"\n✅ API Key found: {api_key[:10]}...")
    
    # Import TTS
    try:
        from utils.ai.tts import GeminiTTS
        print("✅ GeminiTTS imported successfully")
    except Exception as e:
        print(f"❌ Failed to import GeminiTTS: {e}")
        return False
    
    # Initialize TTS
    try:
        tts = GeminiTTS()
        print("✅ GeminiTTS initialized")
    except Exception as e:
        print(f"❌ Failed to initialize GeminiTTS: {e}")
        return False
    
    # Test text processing
    test_texts = [
        "I am doing great, thank you for asking. I have five years of Python development experience.",
        "Hello, my name is John and I am excited about this opportunity.",
        "I have worked on multiple projects using Django, FastAPI, and Flask frameworks."
    ]
    
    print("\n" + "=" * 70)
    print("PROCESSING TEST TEXTS")
    print("=" * 70)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}:")
        print(f"   Original: {text}")
        try:
            processed = tts.generate_speech(text)
            print(f"   ✨ Processed: {processed}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    print("\nGemini TTS is working correctly!")
    print("You can now run the full test with an interview link.")
    return True


if __name__ == "__main__":
    success = test_tts()
    sys.exit(0 if success else 1)
