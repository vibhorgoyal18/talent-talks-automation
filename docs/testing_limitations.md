# Testing Limitations

## Speech Recognition API Simulation

### Challenge
The interview application uses the browser's native Web Speech Recognition API (`window.SpeechRecognition` or `window.webkitSpeechRecognition`) to capture candidate responses. This presents challenges for automated testing:

1. **Native API**: The browser's speech recognition requires real microphone input or cannot be easily mocked after instantiation
2. **Timing**: The interview creates the SpeechRecognition instance when it starts, before test mocks can intercept
3. **Security**: Speech APIs require user gesture and permissions that are difficult to simulate programmatically

### Current Implementation ✅
- ✅ **Transcript Panel**: Can verify the transcript panel opens and displays content
- ✅ **AI Messages**: Can verify AI greeting messages appear in the transcript
- ✅ **Candidate Responses**: Now supported using Chrome DevTools Protocol (CDP) injection

### CDP-Based Solution

The framework now uses **Chrome DevTools Protocol (CDP)** to inject candidate speech responses directly into the browser runtime. This approach:

1. **Creates CDP Session**: Establishes low-level connection to Chrome DevTools
2. **Runtime Evaluation**: Uses `Runtime.evaluate` to execute JavaScript in the page context
3. **Direct Injection**: Searches for active SpeechRecognition instance and triggers `onresult` callback
4. **Fallback Events**: Dispatches custom events if direct injection fails

**Implementation Details:**
- See [interview_page.py](../pages/interview_page.py) → `send_candidate_response()` method
- Uses `page.context.new_cdp_session(page)` to create CDP connection
- Injects mock speech recognition results with 95% confidence
- Waits 3 seconds for response processing

**How it works:**
```python
# CDP injection searches window for SpeechRecognition instance
# Triggers onresult callback with mock transcript
recognition.onresult({
    results: [[{ transcript: "response text", confidence: 0.95, isFinal: true }]],
    resultIndex: 0
})
```

### Workarounds

#### Option 1: Manual Testing
Mark candidate response tests with `@manual` tag and document manual test procedures:

```gherkin
@manual
Scenario: Verify candidate responses appear in transcript
  When I speak "I have five years of Python experience"
  Then the transcript should show my response
```

####Option 2: Pre-inject Mocks
Modify [browser_factory.py](../core/web/browser_factory.py) to inject Speech API mocks before page load:

```python
# In browser_factory.py, add to browser args or page.add_init_script()
await page.add_init_script("""
    window.SpeechRecognition = class MockSpeechRecognition {
        start() {
            setTimeout(() => {
                const event = {
                    results: [[{ transcript: 'Mocked response', confidence: 0.95 }]],
                    resultIndex: 0
                };
                this.onresult(event);
            }, 1000);
        }
        stop() {}
        addEventListener(event, handler) {
            if (event === 'result') this.onresult = handler;
        }
    };
""")
```

#### Option 3: Chrome DevTools Protocol (CDP)
Use CDP to inject fake audio streams (advanced, requires additional setup):

```python
from playwright.sync_api import CDPSession

cdp = page.context.new_cdp_session(page)
# Use CDP commands to simulate audio input
```

#### Option 4: Simplified Verification
Instead of controlling exact text, verify conversation flow:

```gherkin
When I wait for 5 seconds
Then the transcript should contain multiple conversation turns
And the transcript should show both "AI:" and "Candidate:" messages
```

### Recommendation
For now, automated tests verify the transcript infrastructure (panel visibility, AI messages). Full conversation testing should be done manually or with pre-injected mocks in future iterations.

### Related Files
- [create_job_opening.feature](../features/create_job_opening.feature) - Feature file with transcript verification
- [create_job_opening_steps.py](../features/steps/create_job_opening_steps.py) - Step definitions (includes commented candidate response steps)
- [interview_page.py](../pages/interview_page.py) - Page object with transcript methods
- [browser_factory.py](../core/web/browser_factory.py) - Browser initialization (potential location for early mocks)
