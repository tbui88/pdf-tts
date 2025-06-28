"""
Text-to-Speech service using MiniMax TTS API
"""

import os
import asyncio
import logging
import httpx
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSService:
    """MiniMax TTS API integration"""
    
    def __init__(self):
        """Initialize TTS service with MiniMax API configuration"""
        self.api_key = os.getenv("MINIMAX_API_KEY")
        self.group_id = os.getenv("MINIMAX_GROUP_ID")
        self.base_url = "https://api.minimax.chat/v1/t2a_v2"
        
        if not self.api_key:
            logger.warning("MINIMAX_API_KEY not found in environment variables")
        
        if not self.group_id:
            logger.warning("MINIMAX_GROUP_ID not found in environment variables")
        
        # TTS Configuration
        self.tts_config = {
            "voice_id": "female-qn-qingse",  # Default female voice
            "speed": 1.0,  # Normal speed
            "vol": 1.0,    # Normal volume
            "pitch": 0,    # Normal pitch
            "timber_weights": [
                {"voice_id": "female-qn-qingse", "weight": 1}
            ]
        }
        
        # Rate limiting
        self.request_delay = 1.0  # Delay between requests
        self.max_retries = 3
        
    async def text_to_speech(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """
        Convert text to speech using MiniMax TTS API
        
        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID (uses default if not provided)
            
        Returns:
            Audio data as bytes
        """
        if not self.api_key:
            # Fallback to mock audio for testing
            logger.warning("No API key available, generating mock audio")
            return await self._generate_mock_audio(text)
        
        # Prepare request payload
        payload = {
            "text": text,
            "voice_id": voice_id or self.tts_config["voice_id"],
            "speed": self.tts_config["speed"],
            "vol": self.tts_config["vol"],
            "pitch": self.tts_config["pitch"],
            "timber_weights": self.tts_config["timber_weights"]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.group_id:
            headers["X-GroupId"] = self.group_id
        
        # Make API request with retries
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        self.base_url,
                        json=payload,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        # Check if response is audio data or JSON
                        content_type = response.headers.get("content-type", "")
                        
                        if "audio" in content_type:
                            logger.info(f"Successfully converted text to speech (attempt {attempt + 1})")
                            return response.content
                        else:
                            # Response might be JSON with audio URL or base64
                            response_data = response.json()
                            
                            if "audio_file" in response_data:
                                # Download audio from URL
                                audio_url = response_data["audio_file"]
                                audio_response = await client.get(audio_url)
                                if audio_response.status_code == 200:
                                    return audio_response.content
                            
                            elif "audio_data" in response_data:
                                # Base64 encoded audio
                                import base64
                                return base64.b64decode(response_data["audio_data"])
                            
                            else:
                                logger.error(f"Unexpected response format: {response_data}")
                                raise Exception("Unexpected API response format")
                    
                    elif response.status_code == 429:
                        # Rate limit hit, wait longer
                        wait_time = self.request_delay * (2 ** attempt)
                        logger.warning(f"Rate limit hit, waiting {wait_time}s before retry")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    else:
                        logger.error(f"TTS API error: {response.status_code} - {response.text}")
                        if attempt == self.max_retries - 1:
                            raise Exception(f"TTS API failed: {response.status_code}")
                        
                        await asyncio.sleep(self.request_delay)
                        continue
                        
            except httpx.TimeoutException:
                logger.warning(f"TTS API timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise Exception("TTS API timeout")
                await asyncio.sleep(self.request_delay)
                continue
                
            except Exception as e:
                logger.error(f"TTS API error (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"TTS API failed: {str(e)}")
                await asyncio.sleep(self.request_delay)
                continue
        
        # If all retries failed, generate mock audio
        logger.warning("All TTS attempts failed, generating mock audio")
        return await self._generate_mock_audio(text)
    
    async def _generate_mock_audio(self, text: str) -> bytes:
        """
        Generate mock audio for testing when API is not available
        
        Args:
            text: Text that would be converted
            
        Returns:
            Mock MP3 audio data
        """
        # Create a simple MP3 header and silence
        # This is a very basic MP3 file with silence
        duration_seconds = max(1, len(text.split()) // 3)  # Rough estimate: 3 words per second
        
        # Basic MP3 header for silence
        mp3_header = bytes([
            0xFF, 0xFB, 0x90, 0x00,  # MP3 header
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ])
        
        # Add some silence frames
        silence_frame = bytes([0x00] * 144)
        mock_audio = mp3_header + (silence_frame * duration_seconds * 10)
        
        logger.info(f"Generated mock audio of {duration_seconds} seconds for text length {len(text)}")
        return mock_audio
    
    def get_available_voices(self) -> Dict[str, Any]:
        """
        Get list of available voices
        
        Returns:
            Dictionary of available voices
        """
        return {
            "female-qn-qingse": {
                "name": "清澈女声",
                "description": "Clear female voice",
                "language": "zh-CN"
            },
            "male-qn-qingse": {
                "name": "清澈男声", 
                "description": "Clear male voice",
                "language": "zh-CN"
            },
            "female-shaonv": {
                "name": "少女音",
                "description": "Young female voice",
                "language": "zh-CN"
            },
            "male-youthful": {
                "name": "青年男声",
                "description": "Youthful male voice", 
                "language": "zh-CN"
            }
        }
    
    def update_voice_settings(self, **kwargs):
        """
        Update TTS voice settings
        
        Args:
            **kwargs: Voice settings (voice_id, speed, vol, pitch)
        """
        if "voice_id" in kwargs:
            self.tts_config["voice_id"] = kwargs["voice_id"]
            self.tts_config["timber_weights"] = [
                {"voice_id": kwargs["voice_id"], "weight": 1}
            ]
        
        if "speed" in kwargs:
            self.tts_config["speed"] = max(0.5, min(2.0, kwargs["speed"]))
        
        if "vol" in kwargs:
            self.tts_config["vol"] = max(0.1, min(2.0, kwargs["vol"]))
        
        if "pitch" in kwargs:
            self.tts_config["pitch"] = max(-12, min(12, kwargs["pitch"]))
        
        logger.info(f"Updated TTS settings: {self.tts_config}")
    
    async def validate_api_connection(self) -> bool:
        """
        Validate API connection and credentials
        
        Returns:
            True if connection is valid, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            # Test with a short text
            test_text = "Hello, this is a test."
            await self.text_to_speech(test_text)
            return True
        except:
            return False
