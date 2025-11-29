import os
from dotenv import load_dotenv
import requests
import base64

load_dotenv('.env.local')
load_dotenv()

login = os.environ.get('DATAFORSEO_LOGIN')
password = os.environ.get('DATAFORSEO_PASSWORD')

# Test the keyword_ideas endpoint directly
cred = base64.b64encode(f"{login}:{password}".encode('utf-8')).decode('utf-8')
headers = {
    'Authorization': f'Basic {cred}',
    'Content-Type': 'application/json'
}

# Use the exact same config as the code
payload = [{
    "keywords": ["lip plumper"],
    "location_code": 2840,
    "language_code": "en",
    "include_seed_keyword": True,
    "filters": [
        ["keyword_data.keyword_info.search_volume", ">=", 50]
    ],
    "order_by": ["keyword_data.keyword_info.search_volume,desc"],
    "limit": 50
}]

url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_ideas/live"

print("Testing DataForSEO keyword_ideas with 'lip plumper'...")
response = requests.post(url, headers=headers, json=payload, timeout=30)
print(f"Status: {response.status_code}")

data = response.json()
print(f"\nFull response:")
import json
print(json.dumps(data, indent=2)[:1000])

if data.get('tasks') and data['tasks'][0].get('result'):
    results = data['tasks'][0]['result']
    if results and len(results) > 0 and results[0].get('items'):
        print(f"\n✓ GOT {len(results[0]['items'])} KEYWORDS!")
        for item in results[0]['items'][:5]:
            print(f"  - {item.get('keyword')}")
    else:
        print("\n✗ NO ITEMS in result")
        print(f"Result structure: {results}")
else:
    print("\n✗ NO TASKS/RESULT")
