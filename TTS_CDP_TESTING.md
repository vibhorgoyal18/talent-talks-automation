# TTS + CDP Integration Testing

This branch contains scripts to test the integration of Gemini TTS text processing with Chrome DevTools Protocol (CDP) injection for simulating candidate responses in interviews.

## What's New

1. **Gemini TTS Integration** - Uses `google.genai` to process candidate responses naturally
2. **CDP Injection** - Injects processed text into browser's SpeechRecognition API
3. **Test Scripts** - Manual and automated testing tools

## Quick Test (Manual)

### Step 1: Get an Interview Link

Option A - Use existing link from dashboard:
1. Go to https://talenttalks.vlinkinfo.com/dashboard
2. Navigate to "Schedule Interview"
3. Fill the form and set interview time to "now"
4. Copy the generated interview link

Option B - Use the helper script (may be slow):
```bash
python create_quick_interview.py
```

### Step 2: Test TTS + CDP Integration

Run the test script with your interview link:

```bash
python test_interview_response.py
```

When prompted, paste the interview link.

**What it does:**
1. Opens the interview in a browser (headed mode)
2. Starts the interview
3. Opens the transcript panel
4. Uses Gemini TTS to process this text naturally:
   > "I am doing great, thank you for asking. I have five years of Python development experience."
5. Injects the processed response using CDP
6. Checks if the response appears in the transcript
7. Keeps browser open for 30 seconds for manual inspection

## Expected Results

✅ **Success Indicators:**
- Browser opens and navigates to interview
- Transcript panel shows AI greeting
- Gemini processes the candidate response (makes it conversational)
- CDP injects the response
- Response appears in transcript with "Candidate:" prefix

⚠️ **Known Limitations:**
- CDP injection may not work if SpeechRecognition instance isn't accessible
- Transcript may show original text instead of processed text
- Response injection timing depends on interview state

## Files in This Branch

- `test_interview_response.py` - Main test script (interactive)
- `create_quick_interview.py` - Helper to generate interview links
- `test_tts_cdp.py` - Alternate test implementation
- `create_test_interview.py` - Additional helper script
- `get_interview_link.py` - Email-based link retrieval

## Technical Details

### TTS Processing
```python
from utils.ai.tts import GeminiTTS

tts = GeminiTTS()
processed = tts.generate_speech("I have five years of Python experience")
# Returns: "I'm doing great, thanks! I've got five years of Python experience."
```

### CDP Injection
```python
from pages.interview_page import InterviewPage

interview_page.send_candidate_response(processed_text)
# Uses CDP Runtime.evaluate to find SpeechRecognition and trigger onresult
```

## Troubleshooting

**Problem: "TTS not enabled"**
- Check `GEMINI_API_KEY` in `.env`
- Run `python test_tts.py` to verify API key works

**Problem: "Candidate response not found in transcript"**
- CDP injection may have failed
- Check browser console for errors
- Try refreshing and re-running

**Problem: Scripts hang during interview creation**
- Known issue with full E2E flow
- Use manual interview link from dashboard instead

## Next Steps

1. Test with a fresh interview link
2. Verify transcript shows candidate responses
3. Check if responses are natural (Gemini-processed) or original text
4. Document success/failure cases
5. Merge to main if successful

---

**Branch:** `feature/tts-cdp-integration`  
**Status:** Testing in progress  
**Created:** December 22, 2025
