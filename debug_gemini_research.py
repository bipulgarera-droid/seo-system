
import os
import sys
import json
from google import genai
from google.genai import types

# Manual .env parsing
for env_file in ['.env', '.env.local']:
    env_path = f'/Users/bipul/Downloads/seo-saas-brain/{env_file}'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    val = val.strip('"').strip("'")
                    os.environ[key] = val

def perform_gemini_research(topic, location="US", language="English"):
    print(f"Researching: {topic} (Loc: {location})")
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    tool = types.Tool(google_search=types.GoogleSearch())
    
    prompt = f"""
    Research the SEO topic: "{topic}"
    
    **CONTEXT**:
    - Target Audience Location: {location}
    - Target Language: {language}
    
    Perform a deep analysis using Google Search to find:
    1. Top 3 Competitor URLs ranking for this topic in **{location}**.
    2. **At least 30 SEO Keywords** relevant to this topic (include Search Intent).
       - Focus on keywords trending in **{location}**.
       
    Output strictly in JSON format:
    {{
        "competitors": [
            {{"url": "https://...", "title": "Page Title", "domain": "domain.com"}}
        ],
        "keywords": [
            {{"keyword": "keyword phrase", "intent": "Informational/Commercial/Transactional"}}
        ]
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[tool],
                response_mime_type="application/json"
            )
        )
        print(f"Response: {response.text}")
        return json.loads(response.text)
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    topic = "Tipsy Lips Moisturizing Balm - 03 Pinacolada | SUGAR Cosmetics"
    perform_gemini_research(topic, location="India", language="English")
