# Quick Manual Test Instructions

## Get Interview Link (Manual - 2 minutes)

1. **Open dashboard**: https://talenttalks.vlinkinfo.com/login
2. **Login** with:
   - Email: `jitender.sachdeva@vlinkinfo.com`
   - Password: `Vlink@123`
3. **Click** "Schedule Interview" in sidebar
4. **Fill the form**:
   - Select any existing job opening
   - Candidate Name: `Test Candidate`
   - Candidate Email: `test@example.com`
   - Interview Date: Today
   - Interview Time: Set to 1 minute from now (or any time in past/present)
5. **Click** "Schedule Interview" button
6. **Copy the interview link** from the modal/success message
7. **Paste it** when running the test script

## Run Test

```bash
python simple_test.py
```

Paste the interview link when prompted.

## What to Watch

The script will:
1. ✅ Open browser
2. ✅ Navigate to interview
3. ✅ Start interview (if needed)
4. ✅ Open transcript
5. ✅ Process text with Gemini: "I am doing great, thank you for asking. I have five years of Python development experience."
6. 💉 Inject via CDP
7. 🔍 Check if it appears in transcript
8. ⏸️ Keep browser open for 30 seconds

**Expected Success**: You should see the candidate response in the transcript panel with "👤 Candidate:" prefix.

## Alternative: Use Existing Interview

If you have an existing interview link from previous tests, you can use that too. The interview just needs to be active (not ended).
