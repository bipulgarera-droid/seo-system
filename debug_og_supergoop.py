import requests
from bs4 import BeautifulSoup

url = "https://supergoop.com/"
headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
}

print(f"Fetching {url} with Googlebot UA...")
try:
    res = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {res.status_code}")
    
    soup = BeautifulSoup(res.content, 'html.parser')
    
    # Print only OG tags
    print("\nScanning for OG Tags...")
    og_count = 0
    for meta in soup.find_all('meta'):
        prop = meta.get('property', '')
        name = meta.get('name', '')
        if 'og:' in prop or 'og:' in name:
            print(f"FOUND OG: {meta}")
            og_count += 1
            
    print(f"\nTotal OG Tags Found: {og_count}")
        
    # Print Title just to be sure
    if soup.title:
        print(f"Title: {soup.title.string}")

except Exception as e:
    print(f"Error: {e}")
