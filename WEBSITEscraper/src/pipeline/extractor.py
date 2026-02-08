import json
import logging
from datetime import datetime
import google.generativeai as genai
from .models import ESGReport, EnvironmentalData, SocialData, GovernanceData
from ..core.config import settings

import time
import random
from google.api_core import exceptions

logger = logging.getLogger(__name__)

class Extractor:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set. Extraction will fail.")
        else:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                settings.GEMINI_MODEL,
                generation_config={"response_mime_type": "application/json"}
            )

    def extract(self, text: str, url: str) -> ESGReport | None:
        """
        Extracts structured ESG data from text using Gemini.
        """
        if not settings.GEMINI_API_KEY:
            return None

        prompt = f"""
        Analyze the following text for ESG (Environmental, Social, Governance) compliance.
        Extract the data into a JSON object matching this schema:

        {{
            "company_name": "string",
            "url": "{url}",
            "summary": "string",
            "environmental": {{ "score": int, "assessment": "string", "gaps": "string" }},
            "social": {{ "score": int, "assessment": "string", "gaps": "string" }},
            "governance": {{ "score": int, "assessment": "string", "gaps": "string" }},
            "timestamp": "{datetime.now().isoformat()}"
        }}

        Text:
        {text[:30000]} 
        """
        
        retries = 0
        max_retries = 5
        base_delay = 10  # Seconds

        while retries <= max_retries:
            try:
                response = self.model.generate_content(prompt)
                data = json.loads(response.text)
                
                # Validate with Pydantic
                report = ESGReport(**data)
                return report
                
            except exceptions.ResourceExhausted as e:
                retries += 1
                if retries > max_retries:
                    logger.error(f"Quota exceeded for {url}. Max retries reached: {e}")
                    return None
                
                # Calculate backoff with jitter
                delay = (base_delay * (2 ** (retries - 1))) + random.uniform(0, 5)
                logger.warning(f"Quota exceeded for {url}. Retrying in {delay:.2f}s... (Attempt {retries}/{max_retries})")
                time.sleep(delay)

            except Exception as e:
                logger.error(f"Extraction failed for {url}: {e}")
                return None
        
        return None

extractor = Extractor()
