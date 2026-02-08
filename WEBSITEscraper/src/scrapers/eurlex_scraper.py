import asyncio
from playwright.async_api import BrowserContext
from bs4 import BeautifulSoup
from src.utils import get_pdf_text, clean_html_content
from urllib.parse import urljoin

async def scrape_eurlex(context: BrowserContext, base_url: str = "https://eur-lex.europa.eu/homepage.html") -> str:
    """
    Scrapes the EurLex website by searching for ESG/Sustainability keywords.
    """
    print(f"Starting EurLex scrape: {base_url}")
    page = await context.new_page()
    combined_text = ""
    
    # Construct a search URL for "sustainability reporting" directly to save steps
    # Note: EurLex search URLs can be complex. We might try a general search or navigate.
    # Let's try navigating to the search page and typing, or using a known search query structure if possible.
    # For robustness, we'll try to use the quick search bar if available, or just a direct search link.
    
    # Direct search link for "Corporate Sustainability Reporting Directive" (example)
    # https://eur-lex.europa.eu/search.html?scope=EURLEX&text=Corporate+Sustainability+Reporting+Directive&lang=en&type=quick&qid=1697...
    
    search_term = "Corporate Sustainability Reporting Directive"
    search_url = f"https://eur-lex.europa.eu/search.html?scope=EURLEX&text={search_term.replace(' ', '+')}&lang=en&type=quick"
    
    try:
        print(f"Navigating to search results: {search_url}")
        await page.goto(search_url, timeout=60000, wait_until="domcontentloaded")
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract titles and links from search results
        # Look for class "title" or similar in search results
        results = soup.find_all('a', class_='title')
        
        if not results:
             # Fallback to main page simple scrape if search fails or structure changes
            print("No search results found or structure changed. Scraping main page.")
            await page.goto(base_url, timeout=30000)
            combined_text += clean_html_content(await page.content())
        else:
            print(f"Found {len(results)} search results.")
            for i, result in enumerate(results[:3]): # Top 3
                title = result.get_text().strip()
                link = result['href']
                # EurLex links are often relative or JS based.
                # If it starts with ./ or similar, fix it
                if link.startswith('.'):
                    link = link[1:] 
                full_url = "https://eur-lex.europa.eu" + link if not link.startswith('http') else link
                
                print(f"Processing result {i+1}: {title}")
                combined_text += f"\n--- REPORT: {title} ---\n"
                
                try:
                    # Check if it's a PDF link or view page
                    # Eurlex often has "PDF" icons.
                    # For now, visit the result page and scrape text.
                    res_page = await context.new_page()
                    await res_page.goto(full_url, timeout=45000, wait_until="domcontentloaded")
                    res_content = await res_page.content()
                    combined_text += clean_html_content(res_content)
                    await res_page.close()
                except Exception as e:
                    print(f"Error scraping result {full_url}: {e}")
                    
    except Exception as e:
        print(f"Error scraping EurLex: {e}")
    finally:
        await page.close()
        
    return combined_text
