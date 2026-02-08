import asyncio
from playwright.async_api import BrowserContext
from bs4 import BeautifulSoup
from src.utils import get_pdf_text, clean_html_content
from urllib.parse import urljoin

async def scrape_efrag(context: BrowserContext, base_url: str = "https://www.efrag.org/en/sustainability-reporting") -> str:
    """
    Scrapes the EFRAG website, focusing on ESG and Sustainability Reporting.
    """
    print(f"Starting EFRAG scrape: {base_url}")
    page = await context.new_page()
    combined_text = ""
    
    try:
        await page.goto(base_url, timeout=60000, wait_until="domcontentloaded")
        content = await page.content()
        combined_text += f"\n--- MAIN PAGE: {base_url} ---\n"
        combined_text += clean_html_content(content)
        
        # Scrape menu/sub-pages related to CSRD or Standards
        soup = BeautifulSoup(content, 'html.parser')
        links_to_visit = set()
        
        keywords = ["csrd", "esrs", "consultation", "standard"]
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            text = a.get_text().lower()
            
            if any(k in text for k in keywords) and "efrag.org" in full_url:
                links_to_visit.add(full_url)
                
        print(f"Found {len(links_to_visit)} relevant links on EFRAG.")
        
        # Limit to top 3
        for link in list(links_to_visit)[:3]:
            print(f"Visiting sub-page: {link}")
            if link.lower().endswith('.pdf'):
                pdf_text = await get_pdf_text(link)
                combined_text += f"\n--- PDF: {link} ---\n{pdf_text}\n"
            else:
                try:
                    sub_page = await context.new_page()
                    await sub_page.goto(link, timeout=45000, wait_until="domcontentloaded")
                    sub_content = await sub_page.content()
                    combined_text += f"\n--- SUBPAGE: {link} ---\n"
                    combined_text += clean_html_content(sub_content)
                    await sub_page.close()
                except Exception as e:
                    print(f"Error scraping {link}: {e}")
                    
    except Exception as e:
        print(f"Error scraping EFRAG: {e}")
    finally:
        await page.close()
        
    return combined_text
