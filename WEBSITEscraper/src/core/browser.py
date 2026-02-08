from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth.stealth import Stealth
from .config import settings
from .network import network_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserManager:
    """
    Manages Playwright browser instances and contexts with stealth features.
    """
    def __init__(self):
        self.playwright = None
        self.browser: Browser | None = None

    async def start(self):
        """Starts the Playwright engine and browser."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        if not self.browser:
            logger.info("Launching browser...")
            self.browser = await self.playwright.chromium.launch(
                headless=settings.HEADLESS,
                args=["--disable-blink-features=AutomationControlled"] # Basic anti-detection flag
            )

    async def get_new_context(self) -> BrowserContext:
        """
        Creates a new browser context with randomized settings for stealth.
        """
        if not self.browser:
            await self.start()
            
        user_agent = network_manager.get_random_user_agent()
        proxy = network_manager.get_proxy_config()
        
        logger.debug(f"Creating context with UA: {user_agent}, Proxy: {proxy}")
        
        context = await self.browser.new_context(
            user_agent=user_agent,
            proxy=proxy,
            viewport={"width": 1920, "height": 1080}, # Standard desktop resolution
            device_scale_factor=1,
        )
        
        return context

    async def get_new_page(self, context: BrowserContext) -> Page:
        """
        Creates a new page in the given context and applies stealth scripts.
        """
        page = await context.new_page()
        
        if settings.STEALTH_ENABLED:
            stealth = Stealth()
            await stealth.apply_stealth_async(page)
            
        return page

    async def stop(self):
        """Stops the browser and Playwright engine."""
        if self.browser:
            await self.browser.close()
            self.browser = None
            
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

browser_manager = BrowserManager()
