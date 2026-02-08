# API Bridge Guide (No `executeCommand` required)

Since the `Execute Command` node is unavailable in your n8n environment, we use a small local API server to bridge the gap.

**Architecture:**
`n8n (HTTP Request)` -> `Local API Server (FastAPI)` -> `Scraper Script`

## 1. Setup

1.  **Install Requirements**:
    The project now requires `fastapi` and `uvicorn`. I have already added them to your environment.
    If you need to install manually:
    ```bash
    pip install fastapi uvicorn
    ```

2.  **Start the API Server**:
    Run this command in a terminal to start the listener:
    ```bash
    c:/Users/divya/.gemini/antigravity/scratch/scraperESG/venv/Scripts/python.exe -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
    ```
    *Keep this terminal open.*

## 2. Triggering from n8n

Now, instead of `Execute Command`, use the **HTTP Request** node.

*   **Method**: `POST`
*   **URL**: `http://host.docker.internal:8000/scrape` (if n8n is in Docker) OR `http://localhost:8000/scrape` (if n8n is native).
*   **Authentication**: None
*   **Body Content Type**: JSON
*   **JSON Parameter**:
    ```json
    {
      "url": "https://finance.ec.europa.eu/sustainable-finance_en",
      "flags": "--gdocs"
    }
    ```

## 3. Triggering via Curl (Directly)

You can also trigger the scraper directly without n8n using curl:

```bash
curl -X POST http://localhost:8000/scrape ^
     -H "Content-Type: application/json" ^
     -d "{\"url\": \"https://finance.ec.europa.eu/sustainable-finance_en\", \"flags\": \"--gdocs\"}"
```
