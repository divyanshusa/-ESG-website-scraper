import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Warning: GEMINI_API_KEY not found in environment variables.")

def analyze_esg_content(text: str) -> dict:
    """
    Analyzes the provided text for ESG compliance according to EU standards.
    Returns a JSON dictionary with the analysis.
    """
    if not API_KEY:
        return {"error": "API Key missing"}

    genai.configure(api_key=API_KEY)
    
    # Use a model that supports JSON mode if available, or just instruct it well.
    # gemini-flash-lite-latest might work better.
    model = genai.GenerativeModel('gemini-flash-lite-latest')

    prompt = f"""
    You are an expert in ESG (Environmental, Social, and Governance) compliance, specifically focusing on EU regulations such as the EU Taxonomy, SFDR (Sustainable Finance Disclosure Regulation), and CSRD (Corporate Sustainability Reporting Directive).

    Analyze the following text scraped from a company's website. 
    Categorize the information into Environmental, Social, and Governance pillars.
    Evaluate the content for alignment with EU standards.

    For each category (Environmental, Social, Governance), provide:
    1. "score": A confidence score (0-100) indicating how well the text demonstrates compliance or disclosure in this area.
    2. "assessment": A brief summary of the findings, citing specific keywords or topics mentioned (e.g., "Scope 3 emissions", "Board diversity", "Human rights due diligence").
    3. "gaps": Potential missing information required by EU regulations.

    Return the output STRICTLY as a JSON object with the following structure:
    {{
        "company_name": "Inferred Company Name or 'Unknown'",
        "summary": "Overall ESG compliance summary",
        "environmental": {{ "score": 0, "assessment": "...", "gaps": "..." }},
        "social": {{ "score": 0, "assessment": "...", "gaps": "..." }},
        "governance": {{ "score": 0, "assessment": "...", "gaps": "..." }}
    }}

    Text to Analyze:
    {text[:30000]} 
    """ # Truncate to avoid token limits if text is massive, though 1.5 flash handles large context.

    import time
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                print(f"Hit rate limit (429). Waiting 30 seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(30)
            else:
                return {"error": error_str}
    
    return {"error": "Max retries exceeded due to rate limits."}

if __name__ == "__main__":
    # Test with dummy text
    dummy_text = "We are committed to reducing our carbon footprint by 50% by 2030. We follow all labor laws."
    print(json.dumps(analyze_esg_content(dummy_text), indent=2))
