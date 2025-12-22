"""Compatibility wrapper for TTS generator.

This module provides backwards compatibility by importing from the new location.
Prefer importing directly from utils.ai.tts in new code.
"""

import warnings
from utils.ai.tts import GeminiTTS

# Backwards compatibility alias
TTSGenerator = GeminiTTS

warnings.warn(
    "Importing from utils.tts_generator is deprecated. "
    "Please use 'from utils.ai.tts import GeminiTTS' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['TTSGenerator', 'GeminiTTS']
