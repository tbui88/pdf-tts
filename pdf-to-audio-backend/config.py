"""
Configuration management for PDF to Audio API
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings"""
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # API Configuration
    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_GROUP_ID: str = os.getenv("MINIMAX_GROUP_ID", "")
    
    # File Configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    UPLOAD_PATH: str = os.getenv("UPLOAD_PATH", "uploads")
    AUDIO_OUTPUT_PATH: str = os.getenv("AUDIO_OUTPUT_PATH", "audio_output")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
        if origin.strip()
    ]
    
    # TTS Configuration
    DEFAULT_VOICE: str = os.getenv("DEFAULT_VOICE", "female-qn-qingse")
    DEFAULT_SPEED: float = float(os.getenv("DEFAULT_SPEED", "1.0"))
    DEFAULT_VOLUME: float = float(os.getenv("DEFAULT_VOLUME", "1.0"))
    MAX_CHUNK_SIZE: int = int(os.getenv("MAX_CHUNK_SIZE", "2000"))
    
    # Rate Limiting
    TTS_REQUEST_DELAY: float = float(os.getenv("TTS_REQUEST_DELAY", "1.0"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def upload_dir(self) -> Path:
        """Get upload directory path"""
        path = Path(self.UPLOAD_PATH)
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def audio_output_dir(self) -> Path:
        """Get audio output directory path"""
        path = Path(self.AUDIO_OUTPUT_PATH)
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.MINIMAX_API_KEY and not self.DEBUG:
            print("Warning: MINIMAX_API_KEY not set")
        
        return True


# Global settings instance
settings = Settings()
