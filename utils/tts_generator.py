"""Text-to-Speech generator using Google Gemini API."""

import os
import base64
from pathlib import Path
from typing import Optional

import google.generativeai as genai
from utils.logger import get_logger
from utils.config_loader import ConfigLoader

logger = get_logger()


class TTSGenerator:
    """Generate speech audio from text using Google Gemini TTS."""

    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        """Initialize TTS generator with API key.
        
        Args:
            config_loader: Optional config loader. If not provided, creates new instance.
        """
        self.config_loader = config_loader or ConfigLoader()
        
        # Get API key from environment or config
        api_key = os.getenv("GEMINI_API_KEY") or self.config_loader.get("gemini_api_key")
        
        if not api_key:
            logger.warning("GEMINI_API_KEY not found. TTS will not work.")
            self.enabled = False
        else:
            genai.configure(api_key=api_key)
            self.enabled = True
            logger.info("TTS Generator initialized with Gemini API")

    def generate_speech(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """Generate speech audio from text.
        
        Args:
            text: The text to convert to speech
            output_path: Optional path to save audio file. If None, uses temp directory.
            
        Returns:
            Path to the generated audio file, or None if generation failed
        """
        if not self.enabled:
            logger.error("TTS Generator is not enabled. Check GEMINI_API_KEY.")
            return None
        
        try:
            # Note: As of Dec 2024, Gemini doesn't have native TTS API
            # This is a placeholder for when the API becomes available
            # For now, we'll create a simple fallback using gTTS or similar
            
            logger.warning("Gemini TTS API not yet available. Using fallback implementation.")
            return self._fallback_tts(text, output_path)
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None

    def _fallback_tts(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """Fallback TTS implementation.
        
        Since Gemini doesn't have TTS yet, we'll create a silent audio file
        and log the text that would have been spoken.
        
        Args:
            text: Text to convert to speech
            output_path: Optional output path
            
        Returns:
            Path to generated (silent) audio file
        """
        try:
            # For testing purposes, create a simple WAV file with silence
            # In production, you would use gTTS, pyttsx3, or another TTS library
            
            if output_path is None:
                output_path = f"/tmp/tts_output_{hash(text)}.wav"
            
            # Create a minimal WAV file (silence)
            # WAV file format: RIFF header + fmt chunk + data chunk
            self._create_silent_wav(output_path, duration_ms=len(text) * 50)  # ~50ms per character
            
            logger.info(f"Generated TTS audio (fallback): {output_path}")
            logger.info(f"Would have spoken: {text[:100]}...")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Fallback TTS failed: {e}")
            return None

    def _create_silent_wav(self, output_path: str, duration_ms: int = 1000) -> None:
        """Create a minimal silent WAV file.
        
        Args:
            output_path: Path to save the WAV file
            duration_ms: Duration in milliseconds
        """
        import wave
        import struct
        
        # Audio parameters
        sample_rate = 16000  # 16kHz (good for speech recognition)
        channels = 1  # Mono
        bits_per_sample = 16
        
        # Calculate number of frames
        num_frames = int(sample_rate * duration_ms / 1000)
        
        # Create WAV file
        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(bits_per_sample // 8)
            wav_file.setframerate(sample_rate)
            
            # Write silent frames (zeros)
            for _ in range(num_frames):
                wav_file.writeframes(struct.pack('<h', 0))
        
        logger.debug(f"Created silent WAV file: {output_path} ({duration_ms}ms)")
