---
name: WEBSITEscraper
description: Scrapes ESG data from websites using a Playwright crawler and Gemini AI for analysis.
---

# WEBSITEscraper

This skill provides a robust, stealthy web scraper designed to extract and analyze Environmental, Social, and Governance (ESG) data from corporate websites.

## Capabilities

-   **Stealth Scraping**: Uses Playwright with stealth plugins to avoid detection.
-   **Structure Extraction**: Analyzes page content using Gemini AI to extract structured JSON data.
-   **PDF Parsing**: Automatically downloads and extracts text from linked PDF reports.
-   **Rate Limiting**: Built-in exponential backoff to handle API quota limits.

## Usage

### Prerequisites
- Python 3.10+
- Playwright browsers installed (`playwright install`)
- Google Gemini API Key

### Installation

1.  Navigate to the skill directory:
    ```bash
    cd c:/Users/divya/.gemini/antigravity/skills/WEBSITEscraper
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up environment:
    Create a `.env` file with your `GEMINI_API_KEY`.

### Running the Scraper

**Command Line:**
```bash
python src/main.py <URL> --flags <FLAGS>
```

**Example:**
```bash
python src/main.py https://example.com --gdocs
```

**via API (FastAPI):**
1.  Start the server: `run_api.bat`
2.  Send POST request to `http://localhost:8000/scrape` with JSON body `{"url": "...", "flags": "..."}`.

## Files

-   `src/`: Source code including crawler, extractor, and interface.
-   `requirements.txt`: Python dependencies.
-   `run_api.bat`: script to launch the API server.
