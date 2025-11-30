import requests
from bs4 import BeautifulSoup
import json

url = "https://supergoop.com/products/100-mineral-sunscreen-stick"

print("\n--- Testing JSON-LD Schema ---")
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}
try:
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    schemas = soup.find_all('script', type='application/ld+json')
    print(f"Found {len(schemas)} schema tags")
    
    for i, schema in enumerate(schemas):
        try:
            data = json.loads(schema.string)
            print(f"\nSchema #{i+1} Type: {data.get('@type')}")
            if data.get('@type') == 'Product':
                print(f"Name: {data.get('name')}")
                print(f"Description: {data.get('description')}")
                print(f"Image: {data.get('image')}")
        except Exception as e:
            print(f"Schema #{i+1}: Failed to parse JSON: {e}")
            print(f"Raw Content Snippet: {schema.string[:500]}...")

except Exception as e:
    print(f"Request failed: {e}")
