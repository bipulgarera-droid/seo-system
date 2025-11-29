import os
from dotenv import load_dotenv
import requests
import base64

load_dotenv('.env.local')
load_dotenv()

login = os.environ.get('DATAFORSEO_LOGIN')
password = os.environ.get('DATAFORSEO_PASSWORD')

if not login or not password:
    print("✗ DataForSEO credentials not found")
    exit(1)

print(f"✓ Login: {login}")
print(f"✓ Password: ***{password[-4:]}")

# Test API
cred = base64.b64encode(f"{login}:{password}".encode('utf-8')).decode('utf-8')
headers = {
    'Authorization': f'Basic {cred}',
    'Content-Type': 'application/json'
}

# Simple test query
payload = [{
    "language_code": "en",
    "location_code": 2840,  # US
    "keywords": ["lipstick"],
    "search_partners": False,
    "date_from": "2025-01-01"
}]

url = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"

print("\nTesting DataForSEO API...")
try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('tasks') and data['tasks'][0].get('result'):
            results = data['tasks'][0]['result']
            print(f"✓ API WORKS! Got {len(results)} results")
            for r in results[:3]:
                print(f"  - {r.get('keyword')}: {r.get('search_volume')} searches/mo")
        else:
            print(f"✗ No results: {data}")
    else:
        print(f"✗ Error: {response.text}")
except Exception as e:
    print(f"✗ Request failed: {e}")
