import asyncio
from playwright.async_api import Page, BrowserContext
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from src.utils import get_pdf_text, clean_html_content

async def scrape_finance_ec(context: BrowserContext, base_url: str = "https://finance.ec.europa.eu/sustainable-finance_en") -> str:
    """
    Scrapes the Finance EC website, specifically focusing on Sustainable Finance.
    """
    print(f"Starting Finance EC scrape: {base_url}")
    page = await context.new_page()
    combined_text = ""
    
    try:
        await page.goto(base_url, timeout=60000, wait_until="domcontentloaded")
        content = await page.content()
        combined_text += f"\n--- MAIN PAGE: {base_url} ---\n"
        combined_text += clean_html_content(content)
        
        # Find relevant sub-links
        # Look for "Overview", "Disclosures", "Taxonomy" in the navigation or body
        soup = BeautifulSoup(content, 'html.parser')
        links_to_visit = set()
        
        keywords = ["taxonomy", "disclosures", "csrd", "sfdr", "standards"]
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            text = a.get_text().lower()
            
            if any(k in text for k in keywords) and "finance.ec.europa.eu" in full_url:
                links_to_visit.add(full_url)
        
        print(f"Found {len(links_to_visit)} relevant links on Finance EC.")
        
        # Limit to top 3 to avoid timeouts
        for link in list(links_to_visit)[:3]:
            print(f"Visiting sub-page: {link}")
            if link.endswith('.pdf'):
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
        print(f"Error scraping Finance EC: {e}")
    finally:
        await page.close()
        
    return combined_text
