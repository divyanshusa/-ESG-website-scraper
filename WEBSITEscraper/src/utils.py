import requests
import io
from pypdf import PdfReader
from bs4 import BeautifulSoup

def get_pdf_text(url: str) -> str:
    """Downloads a PDF and extracts its text."""
    try:
        print(f"Downloading PDF: {url}")
        # Fake user agent to avoid 403s
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
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

def clean_html_content(html_content: str) -> str:
    """Cleans HTML content specifically for text analysis."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe", "svg"]):
        script.extract()
    
    # Get text
    text = soup.get_text(separator='\n')
    
    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text
