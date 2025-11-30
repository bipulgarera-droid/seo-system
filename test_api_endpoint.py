
import requests
import json
import os
from dotenv import load_dotenv
from api.index import supabase

load_dotenv('.env.local')

API_URL = "http://127.0.0.1:3000/api/batch-update-pages"

# Get a product page
print("Fetching a product page...")
res = supabase.table('pages').select('id, url').eq('page_type', 'Product').limit(1).execute()
if not res.data:
    print("No product pages found.")
    exit()

page_id = res.data[0]['id']
url = res.data[0]['url']
print(f"Testing for Page ID: {page_id} ({url})")

payload = {
    "page_ids": [page_id],
    "action": "generate_content"
}

print(f"Sending POST to {API_URL} with payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(API_URL, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("Success! Check debug.log for background thread activity.")
    else:
        print("Failed!")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure the server is running on port 5000!")
