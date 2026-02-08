from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # --- Network & Robustness ---
    MAX_RETRIES: int = 5
    RETRY_DELAY_BASE: float = 2.0  # Seconds
    REQUEST_TIMEOUT: int = 60000  # Milliseconds (Playwright default)
    CONCURRENCY_LIMIT: int = 5  # Max parallel pages
    
    # --- Scraping Logic ---
    MAX_DEPTH: int = 2
    USER_AGENT_ROTATION: bool = True
    HEADLESS: bool = True
    STEALTH_ENABLED: bool = True
    
    # --- Proxy Configuration ---
    # Use format: "http://user:pass@host:port"
    PROXY_URL: Optional[str] = None 
    # Or provide a list of proxies to rotate through
    PROXY_LIST: List[str] = []

    # --- Data Pipeline ---
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-flash-latest"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
