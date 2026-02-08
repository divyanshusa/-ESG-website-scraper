from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import asyncio
import subprocess
import sys
import os

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str
    flags: str = ""

def run_scraper_task(url: str, flags: str):
    """
    Runs the scraper as a subprocess.
    """
    # Locate the python executable and main script
    python_exe = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), "main.py")
    
    command = [python_exe, script_path, url]
    if flags:
        command.extend(flags.split())
        
    print(f"Executing: {' '.join(command)}")
    
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running scraper: {e}")

@app.post("/scrape")
async def trigger_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to trigger the scraper.
    """
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")

    # Run in background so the API returns immediately
    background_tasks.add_task(run_scraper_task, request.url, request.flags)
    
    return {"status": "accepted", "message": f"Scraper started for {request.url}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
