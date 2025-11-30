import requests
from bs4 import BeautifulSoup

url = "https://supergoop.com/products/100-mineral-sunscreen-stick"

print("\n--- Testing Googlebot UA ---")
headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
}
try:
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    title = soup.find('title')
    og_title = soup.find('meta', property='og:title')
    
    print(f"Title: {title.string if title else 'None'}")
    print(f"OG Title: {og_title['content'] if og_title else 'None'}")
    
    if 'og:title' in r.text:
        print("'og:title' found in raw HTML")
    else:
        print("'og:title' NOT found in raw HTML")
        
except Exception as e:
    print(f"Googlebot request failed: {e}")
