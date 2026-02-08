import asyncio
from typing import Set, List
from urllib.parse import urljoin, urlparse
from collections import deque
from bs4 import BeautifulSoup
import logging

from ..core.browser import BrowserManager
from ..core.config import settings
from ..core.network import network_manager

logger = logging.getLogger(__name__)

class Crawler:
    """
    Robust crawler engine that manages URL queues, depth, and visiting logic.
    """
    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
        self.visited_urls: Set[str] = set()
        self.queue: deque = deque() # Queue of (url, depth) tuples
        self.results: List[dict] = []

    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """
        Validates if a URL should be crawled based on domain restrictions.
        """
        parsed_url = urlparse(url)
        parsed_base = urlparse(base_domain)
        
        # Must be same domain or subdomain
        if parsed_url.netloc != parsed_base.netloc:
             return False
        
        # Skip common non-content extensions
        skip_exts = ['.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.zip']
        if any(url.lower().endswith(ext) for ext in skip_exts):
            return False
            
        return True

    async def crawl(self, start_url: str):
        """
        Main crawling loop.
        """
        logger.info(f"Starting crawl for {start_url}")
        self.queue.append((start_url, 0))
        self.visited_urls.add(start_url)
        
        # Create a browser context for this session
        context = await self.browser_manager.get_new_context()
        page = await self.browser_manager.get_new_page(context)
        
        try:
            while self.queue:
                current_url, depth = self.queue.popleft()
                
                if depth > settings.MAX_DEPTH:
                    continue
                
                logger.info(f"Visiting: {current_url} (Depth: {depth})")
                
                # Polite delay
                await network_manager.natural_delay()
                
                try:
                    await page.goto(current_url, timeout=settings.REQUEST_TIMEOUT, wait_until="domcontentloaded")
                    content = await page.content()
                    
                    # Store result (raw for now, pipeline handles extraction)
                    self.results.append({
                        "url": current_url,
                        "content": content,
                        "depth": depth
                    })
                    
                    # Extract links if not at max depth
                    if depth < settings.MAX_DEPTH:
                        soup = BeautifulSoup(content, 'html.parser')
                        links = soup.find_all('a', href=True)
                        
                        for link in links:
                            href = link['href']
                            full_url = urljoin(current_url, href)
                            
                            # Remove fragments
                            full_url = full_url.split('#')[0]
                            
                            if (full_url not in self.visited_urls and 
                                self.is_valid_url(full_url, start_url)):
                                
                                self.visited_urls.add(full_url)
                                self.queue.append((full_url, depth + 1))
                                
                except Exception as e:
                    logger.error(f"Failed to crawl {current_url}: {e}")
                    # Could add retry logic here if needed
                    
        finally:
            await context.close()
            
        return self.results
