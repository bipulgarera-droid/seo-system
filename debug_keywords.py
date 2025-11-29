import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def debug_keyword_ideas(seed_keyword, location_code=2356):
    login = os.environ.get('DATAFORSEO_LOGIN')
    password = os.environ.get('DATAFORSEO_PASSWORD')
    
    if not login or not password:
        print("Credentials missing")
        return

    url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_ideas/live"
    payload = [{
        "keywords": [seed_keyword],
        "location_code": location_code,
        "language_code": "en",
        "include_seed_keyword": True,
        # Removing filters to see EVERYTHING
        "limit": 5
    }]
    
    print(f"Requesting keywords for '{seed_keyword}' in location {location_code}...")
    try:
        response = requests.post(url, auth=(login, password), json=payload)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print(json.dumps(data, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_keyword_ideas("Incense Cones")
