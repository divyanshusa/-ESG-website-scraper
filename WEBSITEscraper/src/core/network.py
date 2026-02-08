import asyncio
import random
from .config import settings

# Common User Agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

class NetworkManager:
    """
    Handles network-related tasks like rate limiting and user-agent rotation.
    """
    
    @staticmethod
    def get_random_user_agent() -> str:
        """Returns a random user agent string."""
        if not settings.USER_AGENT_ROTATION:
            return USER_AGENTS[0]
        return random.choice(USER_AGENTS)

    @staticmethod
    async def natural_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
        """
        Sleeps for a random amount of time to simulate human behavior.
        """
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    @staticmethod
    def get_proxy_config() -> dict | None:
        """
        Returns a proxy configuration dictionary for Playwright if configured.
        """
        if settings.PROXY_URL:
            return {"server": settings.PROXY_URL}
        
        if settings.PROXY_LIST:
             # Basic rotation logic: pick random proxy for the session
             proxy = random.choice(settings.PROXY_LIST)
             return {"server": proxy}
             
        return None

network_manager = NetworkManager()
