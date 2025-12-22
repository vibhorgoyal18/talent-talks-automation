"""Test script to verify Gemini TTS functionality."""

import os
from dotenv import load_dotenv
from utils.ai.tts import GeminiTTS

# Load environment variables
load_dotenv()

def test_tts():
    """Test the TTS generator with Gemini API."""
    print("=" * 60)
    print("Testing Gemini TTS Generator")
    print("=" * 60)
    
    # Initialize TTS
    print("\n1. Initializing GeminiTTS...")
    tts = GeminiTTS()
    
    if not tts.enabled:
        print("❌ TTS not enabled. Check GEMINI_API_KEY in .env")
        return False
    
    print("✅ TTS Generator initialized successfully")
    print(f"   API Key present: {bool(tts.api_key)}")
    print(f"   LLM available: {tts.llm is not None}")
    
    # Test text processing with LLM
    print("\n2. Testing text processing with LLM...")
    test_text = "I am doing great, thank you for asking. I have five years of Python development experience."
    
    try:
        processed_text = tts.process_text_with_llm(
            test_text, 
            instruction="Make this text more conversational and natural for speech:"
        )
        print(f"✅ LLM processing successful")
        print(f"   Original: {test_text}")
        print(f"   Processed: {processed_text}")
    except Exception as e:
        print(f"❌ LLM processing failed: {e}")
        return False
    
    # Test speech generation (text processing)
    print("\n3. Testing speech text generation...")
    
    try:
        result_text = tts.generate_speech(test_text)
        if result_text:
            print(f"✅ Speech text generation successful")
            print(f"   Output: {result_text[:150]}...")
            print(f"   Length: {len(result_text)} characters")
        else:
            print("❌ Speech generation returned None")
            return False
    except Exception as e:
        print(f"❌ Speech generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ All TTS tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_tts()
    exit(0 if success else 1)
