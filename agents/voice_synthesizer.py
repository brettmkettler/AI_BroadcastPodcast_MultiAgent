from elevenlabs import generate, set_api_key
import os
from typing import Any

class VoiceSynthesizer:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables. Please set it in your .env file.")
        set_api_key(self.api_key)
    
    def synthesize(self, text: str, voice_id: str) -> Any:
        """
        Synthesize text to speech using Eleven Labs API.
        
        Args:
            text (str): The text to synthesize
            voice_id (str): The Eleven Labs voice ID to use
            
        Returns:
            Audio object from Eleven Labs
        """
        try:
            audio = generate(
                text=text,
                voice=voice_id,
                model="eleven_monolingual_v1"
            )
            return audio
        except Exception as e:
            print(f"Error synthesizing voice: {str(e)}")
            return None
