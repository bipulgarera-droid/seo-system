import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

DATAFORSEO_LOGIN = os.environ.get('DATAFORSEO_LOGIN')
DATAFORSEO_PASSWORD = os.environ.get('DATAFORSEO_PASSWORD')

def get_keyword_ideas(seed_keyword, min_volume=50, limit=5):
    if not DATAFORSEO_LOGIN or not DATAFORSEO_PASSWORD:
        print("DataForSEO credentials missing.")
        return []
        
    print(f"Fetching ideas for: {seed_keyword}")
    url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_ideas/live"
    payload = [{
        "keywords": [seed_keyword],
        "location_code": 2840,
        "language_code": "en",
        "include_seed_keyword": True,
        "limit": limit
    }]
    
    try:
        response = requests.post(url, json=payload, auth=(DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD))
        response.raise_for_status()
        data = response.json()
        
        if data['tasks'] and data['tasks'][0]['result']:
            print("✓ API Call Successful")
            items = data['tasks'][0]['result'][0]['items']
            print(f"Found {len(items)} keywords")
            return items
        else:
            print("✗ No results found")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    print("Testing DataForSEO...")
    get_keyword_ideas("affirmation cards")
