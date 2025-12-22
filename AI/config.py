"""
Configuration for AI module
"""
import os
from dotenv import load_dotenv

load_dotenv()


class AIConfig:
    """AI Module Configuration"""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Gemini Default Settings
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("DEFAULT_MAX_TOKENS", "1000"))
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required but not set in environment variables")


# Create singleton instance
ai_config = AIConfig()

