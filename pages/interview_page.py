from __future__ import annotations

from core.web.playwright_wrapper import PlaywrightWrapper


class InterviewPage:
    """Page Object for the Interview page (candidate-facing interview interface)."""

    # Interview start indicators
    INTERVIEW_HEADING = "role=heading[name*='TalentTalks']"
    WELCOME_HEADING = "role=heading[name='Welcome to Your TalentTalks']"
    
    # Interview controls
    START_INTERVIEW_BUTTON = "role=button[name*='Start Interview']"
    
    # Page elements indicating interview page
    HOW_IT_WORKS_HEADING = "role=heading[name='How It Works']"
    TECH_CHECK_HEADING = "role=heading[name='Quick Tech Check']"
    
    # Error messages
    ACCESS_DENIED_HEADING = "role=heading[name='Access Denied']"
    ACCESS_DENIED_TEXT = "text=Interview link not yet active"
    
    # Interview Guidelines Modal
    GUIDELINES_MODAL = "text=Interview Guidelines"
    GUIDELINES_HEADING = "role=heading[name='Interview Guidelines']"
    CONTINUE_BUTTON = "role=button[name='Continue']"
    CLOSE_GUIDELINES_BUTTON = "role=button[name='Close Guidelines']"
    
    # Interview active indicators (after starting)
    VIDEO_ELEMENT = "video"
    CAMERA_PERMISSION_TEXT = "text=Camera, text=Microphone"
    INTERVIEW_QUESTION_HEADING = "role=heading"  # Questions appear as headings during interview
    RECORDING_INDICATOR = "text=Recording, text=REC"
    
    # Transcript controls
    SHOW_TRANSCRIPTS_BUTTON = "role=button[name*='Show Transcripts']"
    HIDE_TRANSCRIPTS_BUTTON = "role=button[name*='Hide Transcripts']"
    TRANSCRIPT_CONTENT = "p"  # Transcript appears in paragraph elements

    def __init__(self, wrapper: PlaywrightWrapper) -> None:
        self.wrapper = wrapper

    def navigate_to(self, url: str) -> None:
        """Navigate to the interview URL."""
        self.wrapper.go_to(url)

    def is_interview_page_loaded(self) -> bool:
        """Check if the interview page is loaded by looking for interview-related elements.
        Returns False if Access Denied page is shown."""
        try:
            page = self.wrapper.page
            
            # Wait for page to load
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            
            # First check if we got an Access Denied message
            if page.locator(self.ACCESS_DENIED_HEADING).first.is_visible(timeout=2000):
                return False
            
            # Check for welcome heading (main indicator)
            if page.locator(self.WELCOME_HEADING).first.is_visible(timeout=5000):
                return True
            
            # Check for TalentTalks heading as fallback
            if page.locator(self.INTERVIEW_HEADING).first.is_visible(timeout=5000):
                return True
                
            # Check for "How It Works" section
            if page.locator(self.HOW_IT_WORKS_HEADING).first.is_visible(timeout=5000):
                return True
            
            return False
        except Exception:
            return False

    def is_interview_started(self) -> bool:
        """Check if the interview has started or is ready to start."""
        try:
            page = self.wrapper.page
            
            # Check if there's a start button (interview ready but not started)
            start_button = page.locator(self.START_INTERVIEW_BUTTON).first
            if start_button.is_visible(timeout=3000):
                return True  # Interview is ready to start
            
            # Check for tech check section (indicates interview page is ready)
            if page.locator(self.TECH_CHECK_HEADING).first.is_visible(timeout=3000):
                return True
            
            return False
        except Exception:
            return False

    def get_page_title(self) -> str:
        """Get the page title."""
        return self.wrapper.page.title()

    def get_current_url(self) -> str:
        """Get the current URL."""
        return self.wrapper.page.url

    def has_interview_parameter(self) -> bool:
        """Check if the URL contains interview-related parameters."""
        url = self.get_current_url()
        return "interview" in url.lower() and ("interviewId" in url or "name" in url)

    def is_access_denied(self) -> bool:
        """Check if the page shows Access Denied message."""
        try:
            page = self.wrapper.page
            return page.locator(self.ACCESS_DENIED_HEADING).first.is_visible(timeout=2000)
        except Exception:
            return False

    def get_access_denied_message(self) -> str:
        """Get the Access Denied error message if present."""
        try:
            page = self.wrapper.page
            if page.locator(self.ACCESS_DENIED_TEXT).first.is_visible(timeout=2000):
                return page.locator(self.ACCESS_DENIED_TEXT).first.text_content()
            return ""
        except Exception:
            return ""

    def click_start_interview(self) -> None:
        """Click the Start Interview button and handle the guidelines modal if it appears."""
        page = self.wrapper.page
        start_button = page.locator(self.START_INTERVIEW_BUTTON).first
        start_button.click(timeout=10000)
        
        # Wait for guidelines modal to appear
        page.wait_for_timeout(2000)
        
        # Check if guidelines modal appeared and click Continue
        try:
            if page.locator(self.GUIDELINES_HEADING).first.is_visible(timeout=3000):
                continue_button = page.locator(self.CONTINUE_BUTTON).first
                continue_button.click(timeout=5000)
                page.wait_for_timeout(2000)
                
                # After dismissing guidelines modal, click Start Interview button again
                # This second click triggers screen sharing and starts the interview
                start_button_after = page.locator(self.START_INTERVIEW_BUTTON).first
                if start_button_after.is_visible(timeout=3000):
                    start_button_after.click(timeout=10000)
                    # Wait longer for screen sharing permissions and interview to start
                    page.wait_for_timeout(8000)
        except Exception:
            # Modal may not appear or already closed
            pass

    def has_interview_started_after_click(self) -> bool:
        """
        Check if the interview has actually started after clicking the button.
        The interview starts when we transition away from the welcome page OR when video elements appear.
        """
        try:
            page = self.wrapper.page
            
            # Wait for page transition or video to load
            page.wait_for_timeout(3000)
            
            # Check we're not on an error page
            if self.is_access_denied():
                return False
            
            # Check if welcome heading is gone (indicates page transitioned)
            try:
                welcome_visible = page.locator(self.WELCOME_HEADING).first.is_visible(timeout=2000)
            except:
                welcome_visible = False
            
            # Check if start button is gone
            try:
                start_button_visible = page.locator(self.START_INTERVIEW_BUTTON).first.is_visible(timeout=2000)
            except:
                start_button_visible = False
            
            # If both welcome heading and start button are gone, interview has started/transitioned
            if not welcome_visible and not start_button_visible:
                return True
            
            # Check for video element (camera feed) - this indicates screen sharing started
            try:
                video_count = page.locator(self.VIDEO_ELEMENT).count()
                if video_count > 0:
                    video_visible = page.locator(self.VIDEO_ELEMENT).first.is_visible(timeout=3000)
                    if video_visible:
                        return True
            except:
                pass
            
            # Check if URL changed (some apps navigate after starting)
            current_url = page.url
            if "interview" in current_url and ("started" in current_url or "active" in current_url):
                return True
            
            return False
        except Exception:
            return False

    def get_interview_state_info(self) -> dict:
        """Get information about the current state of the interview page for debugging."""
        page = self.wrapper.page
        return {
            "url": page.url,
            "title": page.title(),
            "has_welcome_heading": page.locator(self.WELCOME_HEADING).first.is_visible(timeout=1000) if page.locator(self.WELCOME_HEADING).count() > 0 else False,
            "has_start_button": page.locator(self.START_INTERVIEW_BUTTON).first.is_visible(timeout=1000) if page.locator(self.START_INTERVIEW_BUTTON).count() > 0 else False,
            "has_video_element": page.locator(self.VIDEO_ELEMENT).first.is_visible(timeout=1000) if page.locator(self.VIDEO_ELEMENT).count() > 0 else False,
            "has_access_denied": self.is_access_denied()
        }
    def click_show_transcripts(self) -> None:
        """Click the Show Transcripts button to display the transcript panel."""
        page = self.wrapper.page
        show_button = page.locator(self.SHOW_TRANSCRIPTS_BUTTON).first
        show_button.click(timeout=5000)
        page.wait_for_timeout(1000)

    def is_transcript_panel_visible(self) -> bool:
        """Check if the transcript panel is visible (by checking for Hide Transcripts button)."""
        try:
            page = self.wrapper.page
            hide_button = page.locator(self.HIDE_TRANSCRIPTS_BUTTON).first
            return hide_button.is_visible(timeout=2000)
        except Exception:
            return False

    def get_transcript_content(self) -> list[str]:
        """Get all transcript content from the page."""
        page = self.wrapper.page
        transcript_elements = page.locator(self.TRANSCRIPT_CONTENT).all()
        
        transcript_lines = []
        for element in transcript_elements:
            text = element.text_content()
            if text and ("AI:" in text or "👤" in text or "Candidate:" in text):
                transcript_lines.append(text.strip())
        
        return transcript_lines

    def send_candidate_response(self, response_text: str, audio_file_path: str = None) -> None:
        """Send a candidate response by injecting audio into the browser's microphone stream.
        
        This method creates a fake audio stream from an audio file and feeds it to the
        browser as if it came from the microphone, allowing the SpeechRecognition API
        to process it naturally.
        
        Args:
            response_text: The text of the response (used for logging/fallback)
            audio_file_path: Path to the audio file to play. If None, will use text-based injection.
        """
        page = self.wrapper.page
        
        if audio_file_path:
            # Use audio file injection approach
            self._inject_audio_file(audio_file_path, response_text)
        else:
            # Fallback to text-based CDP injection (current approach)
            self._inject_text_via_cdp(response_text)
    
    def _inject_text_via_cdp(self, response_text: str) -> None:
        """Legacy approach: Inject text directly via CDP (may not work with real SpeechRecognition)."""
        page = self.wrapper.page
        cdp = page.context.new_cdp_session(page)
        
        try:
            # Use CDP Runtime.evaluate to inject the response directly
            result = cdp.send("Runtime.evaluate", {
                "expression": f"""
                    (function() {{
                        const responseText = {repr(response_text)};
                        
                        // Strategy 1: Find and trigger SpeechRecognition instance
                        let foundRecognition = false;
                        
                        // Search for SpeechRecognition instances in window
                        for (let prop in window) {{
                            try {{
                                const obj = window[prop];
                                if (obj && typeof obj === 'object') {{
                                    const constructor = obj.constructor;
                                    if (constructor && 
                                        (constructor.name === 'SpeechRecognition' ||
                                         constructor.name === 'webkitSpeechRecognition')) {{
                                        
                                        // Found an instance! Trigger onresult
                                        if (obj.onresult) {{
                                            const mockEvent = {{
                                                results: [[
                                                    {{
                                                        transcript: responseText,
                                                        confidence: 0.95,
                                                        isFinal: true
                                                    }}
                                                ]],
                                                resultIndex: 0,
                                                type: 'result'
                                            }};
                                            
                                            mockEvent.results[0].isFinal = true;
                                            mockEvent.results.length = 1;
                                            
                                            obj.onresult(mockEvent);
                                            foundRecognition = true;
                                            
                                            console.log('[CDP] Triggered SpeechRecognition.onresult');
                                        }}
                                    }}
                                }}
                            }} catch (e) {{
                                // Ignore property access errors
                            }}
                        }}
                        
                        // Strategy 2: Try React's internal instance
                        if (!foundRecognition) {{
                            const reactRoot = document.querySelector('[data-reactroot], #root, #app');
                            if (reactRoot && reactRoot._reactRootContainer) {{
                                // React 16/17 approach - traverse fiber tree
                                console.log('[CDP] Attempting React fiber traversal...');
                            }}
                        }}
                        
                        // Strategy 3: Dispatch custom event for app to handle
                        document.dispatchEvent(new CustomEvent('mockCandidateResponse', {{
                            detail: {{
                                transcript: responseText,
                                confidence: 0.95,
                                timestamp: Date.now()
                            }}
                        }}));
                        
                        console.log('[CDP] Dispatched mockCandidateResponse event');
                        
                        return {{
                            success: true,
                            foundRecognition: foundRecognition,
                            transcript: responseText
                        }};
                    }})()
                """,
                "returnByValue": True,
                "awaitPromise": False
            })
            
            # Log the result
            if result.get("result", {}).get("value", {}).get("foundRecognition"):
                print(f"✓ Successfully injected candidate response via SpeechRecognition")
            else:
                print(f"⚠ Fallback: Dispatched custom event for response")
            
            # Wait for the response to be processed
            page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"⚠ CDP injection failed: {e}")
            print(f"Attempting direct page.evaluate fallback...")
            
            # Fallback to regular page.evaluate
            page.evaluate("""
                (responseText) => {
                    document.dispatchEvent(new CustomEvent('mockCandidateResponse', {
                        detail: {
                            transcript: responseText,
                            confidence: 0.95,
                            timestamp: Date.now()
                        }
                    }));
                    console.log('[Fallback] Dispatched mockCandidateResponse');
                }
            """, response_text)
            
            page.wait_for_timeout(3000)
            
        finally:
            # Always detach CDP session
            try:
                cdp.detach()
            except:
                pass
    
    def _inject_audio_file(self, audio_file_path: str, response_text: str) -> None:
        """Inject an audio file into the browser's microphone stream.
        
        This creates a fake MediaStream from an audio file and overrides getUserMedia
        to provide this stream instead of the real microphone.
        
        Args:
            audio_file_path: Path to the audio file (WAV, MP3, etc.)
            response_text: The text content (for logging)
        """
        page = self.wrapper.page
        
        # First, read the audio file and convert to base64
        import base64
        import os
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        with open(audio_file_path, 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Determine MIME type from file extension
        ext = os.path.splitext(audio_file_path)[1].lower()
        mime_types = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.ogg': 'audio/ogg',
            '.webm': 'audio/webm'
        }
        mime_type = mime_types.get(ext, 'audio/wav')
        
        # Inject JavaScript to feed audio into the existing microphone stream
        result = page.evaluate("""
            async (audioData, mimeType, responseText) => {
                console.log('[Audio Injection] Checking for active SpeechRecognition...');
                
                // First, find the SpeechRecognition instance
                let recognition = null;
                for (let key in window) {
                    try {
                        if (window[key] && 
                            typeof window[key] === 'object' && 
                            (window[key].constructor.name === 'SpeechRecognition' || 
                             window[key].constructor.name === 'webkitSpeechRecognition')) {
                            recognition = window[key];
                            console.log('[Audio Injection] Found SpeechRecognition instance');
                            break;
                        }
                    } catch (e) {
                        // Skip
                    }
                }
                
                // Throw error if no SpeechRecognition exists
                if (!recognition) {
                    throw new Error('No active SpeechRecognition instance found. Interview must be started first.');
                }
                
                console.log('[Audio Injection] Preparing to inject audio into existing microphone stream...');
                console.log('[Audio Injection] Response text:', responseText);
                
                // Create audio blob from base64 data
                const binaryString = atob(audioData);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
                const audioBlob = new Blob([bytes], { type: mimeType });
                const audioUrl = URL.createObjectURL(audioBlob);
                
                // Create audio element
                const audio = new Audio(audioUrl);
                
                // Wait for audio metadata to load
                await new Promise((resolve) => {
                    audio.onloadedmetadata = () => resolve();
                    audio.load();
                });
                
                console.log('[Audio Injection] Audio duration:', audio.duration, 'seconds');
                
                // Create AudioContext and fake microphone stream
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const destination = audioContext.createMediaStreamDestination();
                
                // Create source from audio file and connect to destination
                const source = audioContext.createMediaElementSource(audio);
                source.connect(destination);
                source.connect(audioContext.destination); // For debugging
                
                // Store original getUserMedia
                const originalGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
                
                // Override getUserMedia to return our audio stream
                navigator.mediaDevices.getUserMedia = async function(constraints) {
                    console.log('[Audio Injection] getUserMedia intercepted');
                    
                    if (constraints && constraints.audio) {
                        console.log('[Audio Injection] Returning fake audio stream');
                        await audio.play();
                        return destination.stream;
                    }
                    
                    return originalGetUserMedia(constraints);
                };
                
                // Stop current recognition
                console.log('[Audio Injection] Stopping current SpeechRecognition...');
                try {
                    recognition.stop();
                } catch (e) {
                    console.log('[Audio Injection] Recognition stop error (may already be stopped):', e);
                }
                
                // Wait for recognition to stop
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // Start playing the audio
                console.log('[Audio Injection] Playing audio...');
                await audio.play();
                
                // Restart recognition - it will call getUserMedia and get our fake stream
                console.log('[Audio Injection] Restarting SpeechRecognition with fake microphone...');
                try {
                    recognition.start();
                    console.log('[Audio Injection] SpeechRecognition restarted successfully');
                } catch (e) {
                    throw new Error('Failed to restart SpeechRecognition: ' + e.message);
                }
                
                return {
                    success: true,
                    duration: audio.duration,
                    message: 'Audio injected into existing microphone stream'
                };
            }
        """, audio_data, mime_type, response_text)
        
        if not result or not result.get('success'):
            raise Exception("Failed to inject audio into microphone stream")
        
        print(f"✓ Injected audio file: {audio_file_path}")
        print(f"✓ SpeechRecognition should now process this audio")
        
        # Wait for audio to play and be processed
        # TODO: Get actual audio duration and wait for that
        page.wait_for_timeout(5000)