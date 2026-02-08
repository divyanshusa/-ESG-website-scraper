import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import sys
import requests
import io
from pypdf import PdfReader
from urllib.parse import urljoin, urlparse

async def get_pdf_text(url: str) -> str:
    """Downloads a PDF and extracts its text."""
    try:
        print(f"Downloading PDF: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with io.BytesIO(response.content) as f:
            reader = PdfReader(f)
            text = ""
            # Limit to first 50 pages to avoid massive processing time
            for i, page in enumerate(reader.pages[:50]):
                text += page.extract_text() + "\n"
            print(f"Extracted {len(text)} chars from PDF.")
            return text
    except Exception as e:
        print(f"Error reading PDF {url}: {e}")
        return ""

async def scrape_website(url: str, depth: int = 1) -> str:
    """Scrapes the website, crawls for ESG keywords, and parses PDFs."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            
            print(f"Navigating to {url}...")
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            
            # 1. Scrape Main Page
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Clean text from main page
            for script in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe"]):
                script.extract()
            main_text = soup.get_text(separator='\n')
            
            # 2. Find Relevant Links (Crawling)
            keywords = ["sustainability", "esg", "environment", "social", "governance", "report", "2024", "2023", "non-financial"]
            links_to_visit = set()
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(url, href)
                text = a.get_text().lower()
                
                # Check for keywords in link text or URL
                if any(k in text for k in keywords) or any(k in full_url.lower() for k in keywords):
                    # Ensure it's the same domain or subdomain
                    if urlparse(full_url).netloc == urlparse(url).netloc or ".pdf" in full_url:
                        links_to_visit.add(full_url)
            
            print(f"Found {len(links_to_visit)} potential relevant links.")
            
            combined_text = f"--- MAIN PAGE CONTENT ---\n{main_text}\n"
            
            # 3. Visit Links (PDFs or Pages)
            # Limit to 5 relevant links to save time/resources for now
            for link in list(links_to_visit)[:5]:
                print(f"Processing link: {link}")
                
                if link.lower().endswith('.pdf'):
                    pdf_text = await get_pdf_text(link)
                    combined_text += f"\n--- PDF CONTENT: {link} ---\n{pdf_text}\n"
                else:
                    try:
                        # Scrape sub-page
                        sub_page = await context.new_page()
                        await sub_page.goto(link, timeout=30000, wait_until="domcontentloaded")
                        sub_content = await sub_page.content()
                        await sub_page.close()
                        
                        sub_soup = BeautifulSoup(sub_content, 'html.parser')
                        for script in sub_soup(["script", "style", "nav", "footer", "header", "noscript", "iframe"]):
                            script.extract()
                        sub_text = sub_soup.get_text(separator='\n')
                        combined_text += f"\n--- SUBPAGE CONTENT: {link} ---\n{sub_text}\n"
                    except Exception as e:
                        print(f"Failed to scrape subpage {link}: {e}")

            # Clean up whitespace
            lines = (line.strip() for line in combined_text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            final_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return final_text
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return ""
        finally:
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <URL>")
        sys.exit(1)
        
    url = sys.argv[1]
    result = asyncio.run(scrape_website(url))
    print("\n--- Scraped Content ---\n")
    print(result)
