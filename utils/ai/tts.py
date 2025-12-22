"""Text-to-Speech generator using Google Gemini API and LangChain."""

import os
from pathlib import Path
from typing import Optional

from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.logger import get_logger
from utils.config_loader import ConfigLoader

logger = get_logger()


class GeminiTTS:
    """Generate speech audio from text using Google Gemini API with LangChain."""

    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        """Initialize TTS generator with API key.
        
        Args:
            config_loader: Optional config loader. If not provided, creates new instance.
        """
        self.config_loader = config_loader or ConfigLoader()
        
        # Get API key from environment or config
        self.api_key = os.getenv("GEMINI_API_KEY") or self.config_loader.get("gemini_api_key")
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. TTS will not work.")
            self.enabled = False
            self.client = None
            self.llm = None
        else:
            # Initialize Gemini client
            try:
                self.client = genai.Client(api_key=self.api_key)
                
                # Initialize LangChain LLM for text processing
                # Using gemini-2.5-flash (stable model)
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=self.api_key,
                    temperature=0.7
                )
                self.enabled = True
                logger.info("TTS Generator initialized with Gemini API (google.genai) and LangChain")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.enabled = False
                self.client = None
                self.llm = None

    def generate_speech(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """Generate speech audio from text using Gemini.
        
        Note: Currently returns the processed text for CDP injection.
        When Gemini TTS API becomes available, this will generate actual audio.
        
        Args:
            text: The text to convert to speech
            output_path: Optional path to save audio file (reserved for future use)
            
        Returns:
            Processed text ready for speech synthesis, or None if processing failed
        """
        if not self.enabled:
            logger.error("TTS Generator is not enabled. Check GEMINI_API_KEY.")
            return None
        
        try:
            # Process text with LLM to make it more natural for speech
            processed_text = self.process_text_with_llm(
                text,
                instruction="Convert this text to natural, conversational speech. Keep it concise and natural."
            )
            
            logger.info(f"Processed text for speech: {processed_text[:100]}...")
            
            # Return the processed text for CDP injection
            # When Gemini TTS API is available, we'll generate audio here
            return processed_text
            
        except Exception as e:
            logger.error(f"Error processing text for speech: {e}")
            return text  # Return original text as fallback

    def process_text_with_llm(self, text: str, instruction: str = "Simplify this text for speech:") -> str:
        """Process text using LangChain LLM before TTS conversion.
        
        Args:
            text: The text to process
            instruction: Instruction for the LLM on how to process the text
            
        Returns:
            Processed text ready for TTS, or original text if processing fails
        """
        if not self.llm:
            logger.warning("LLM not available. Returning original text.")
            return text
        
        try:
            from langchain_core.messages import HumanMessage
            
            messages = [HumanMessage(content=f"{instruction}\n\n{text}")]
            response = self.llm.invoke(messages)
            
            processed_text = response.content if hasattr(response, 'content') else str(response)
            logger.info(f"Processed text with LLM: {processed_text[:100]}...")
            return processed_text
            
        except Exception as e:
            logger.error(f"LLM text processing failed: {e}")
            return text


