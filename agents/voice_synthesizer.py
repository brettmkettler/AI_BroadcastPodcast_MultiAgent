from elevenlabs import generate, set_api_key
import os
from typing import Any, Tuple
import math

class VoiceSynthesizer:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables. Please set it in your .env file.")
        set_api_key(self.api_key)
    
    def synthesize(self, text: str, voice_id: str) -> Tuple[bytes, float]:
        """
        Synthesize text to speech using Eleven Labs API.
        
        Args:
            text (str): The text to synthesize
            voice_id (str): The Eleven Labs voice ID to use
            
        Returns:
            Tuple[bytes, float]: Audio data and estimated duration in seconds
        """
        try:
            audio = generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2"
            )
            
            # Estimate duration based on text length and average speaking rate
            # Average speaking rate is about 150 words per minute
            words = len(text.split())
            estimated_duration = (words / 150) * 60  # Convert to seconds
            
            # Add padding for very short texts
            estimated_duration = max(estimated_duration, 2.0)
            
            return audio, estimated_duration
            
        except Exception as e:
            print(f"Error synthesizing voice: {str(e)}")
            return None, 0
