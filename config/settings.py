"""Application settings and configuration."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # Project paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    USERS_DIR: Path = DATA_DIR / "users"
    CACHE_DIR: Path = DATA_DIR / "cache"
    
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Browser Settings
    HEADLESS_MODE: bool = os.getenv("HEADLESS_MODE", "false").lower() == "true"
    BROWSER_TIMEOUT: int = int(os.getenv("BROWSER_TIMEOUT", "30"))
    
    # Chrome Connection Settings
    USE_EXISTING_CHROME: bool = os.getenv("USE_EXISTING_CHROME", "true").lower() == "true"
    CHROME_DEBUGGER_PORT: int = int(os.getenv("CHROME_DEBUGGER_PORT", "9222"))
    
    # Chrome Profile Settings (fallback if existing Chrome not available)
    USE_CHROME_PROFILE: bool = os.getenv("USE_CHROME_PROFILE", "true").lower() == "true"
    CHROME_PROFILE_NAME: str = os.getenv("CHROME_PROFILE_NAME", "Default")  # Or "Profile 1", "Profile 2", etc.
    
    # Platform URLs
    SWIGGY_URL: str = os.getenv("SWIGGY_URL", "https://www.swiggy.com")
    ZOMATO_URL: str = os.getenv("ZOMATO_URL", "https://www.zomato.com")
    BLINKIT_URL: str = os.getenv("BLINKIT_URL", "https://www.blinkit.com")
    
    # User Settings
    DEFAULT_USER_ID: str = os.getenv("DEFAULT_USER_ID", "user_001")
    
    # Cache Settings
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_EXPIRY_HOURS: int = int(os.getenv("CACHE_EXPIRY_HOURS", "24"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __init__(self):
        """Initialize settings and create necessary directories."""
        self.USERS_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """Validate that all required settings are present."""
        if not self.GEMINI_API_KEY:
            return False
        return True
    
    def get_user_file(self, user_id: str) -> Path:
        """Get the path to a user's data file."""
        return self.USERS_DIR / f"{user_id}.json"
    
    def get_cache_file(self, cache_key: str) -> Path:
        """Get the path to a cache file."""
        return self.CACHE_DIR / f"{cache_key}.json"

# Global settings instance
settings = Settings()
