@echo off
cd /d "c:\Users\divya\.gemini\antigravity\scratch\scraperESG"
set PYTHONPATH=%CD%
.\venv\Scripts\python.exe -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
pause
