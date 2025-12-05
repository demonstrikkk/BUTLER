"""Configuration settings for BUTLER agent."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Global settings for the application."""
    
    # Base directories
    BASE_DIR = Path(__file__).parent.parent
    CONFIG_DIR = BASE_DIR / "config"
    DATA_DIR = BASE_DIR / "data"
    AGENT_DIR = BASE_DIR / "agent"
    
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "users").mkdir(exist_ok=True)
    
    # Google Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Browser settings
    HEADLESS_MODE = os.getenv("HEADLESS_MODE", "false").lower() == "true"
    BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30"))
    BROWSER_WIDTH = int(os.getenv("BROWSER_WIDTH", "1920"))
    BROWSER_HEIGHT = int(os.getenv("BROWSER_HEIGHT", "1080"))
    
    # Debug mode
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Supported platforms
    SUPPORTED_PLATFORMS = ["swiggy", "zomato", "blinkit"]
    
    # Platform URLs
    PLATFORM_URLS = {
        "swiggy": "https://www.swiggy.com",
        "zomato": "https://www.zomato.com",
        "blinkit": "https://www.blinkit.com"
    }
    
    # Default timeouts (in seconds)
    ELEMENT_WAIT_TIMEOUT = 10
    PAGE_LOAD_TIMEOUT = 20
    
    # Data file paths
    def get_user_data_path(self, user_id: str, data_type: str) -> Path:
        """Get path for user data files."""
        return self.DATA_DIR / "users" / f"{user_id}_{data_type}.json"

# Global settings instance
settings = Settings()
