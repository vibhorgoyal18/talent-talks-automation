Feature: Test TTS + CDP Integration
    As a developer
    I want to test Gemini TTS processing and CDP injection
    So that I can verify candidate responses work correctly

    @tts @cdp @smoke
    Scenario: Send candidate response using Gemini TTS and CDP injection
    # This test requires a valid interview link to be provided via environment variable
    # Set INTERVIEW_LINK environment variable before running:
    # export INTERVIEW_LINK="https://talenttalks.vlinkinfo.com/interview?name=...&interviewId=..."

    Given I have an active interview link
        When I open the interview link
            Then the interview page should load successfully

        When I click the Start Interview button
            Then the interview should actually start
        When I wait for 2 seconds

        When I click the "Show Transcripts" button in the interview
            Then the transcript panel should be visible
            And the transcript should contain the AI greeting message

        When I send candidate response "I am doing great, thank you for asking. I have five years of Python development experience."
            And I wait for 3 seconds
            Then the transcript should contain the candidate response
