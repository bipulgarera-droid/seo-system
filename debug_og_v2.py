import subprocess
import requests
from bs4 import BeautifulSoup

url = "https://supergoop.com/products/100-mineral-sunscreen-stick"

def check_html(html, method):
    if not html:
        print(f"[{method}] Failed to get HTML")
        return

    soup = BeautifulSoup(html, 'html.parser')
    og_title = soup.find('meta', property='og:title')
    title = soup.find('title')
    
    print(f"[{method}] Title: {title.string if title else 'None'}")
    print(f"[{method}] OG Title: {og_title['content'] if og_title else 'None'}")
    
    # Check raw string just in case
    if 'og:title' in html:
        print(f"[{method}] 'og:title' found in raw HTML")
    else:
        print(f"[{method}] 'og:title' NOT found in raw HTML")

# 1. Requests with Browser Headers
print("\n--- Testing requests ---")
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/'
}
try:
    r = requests.get(url, headers=headers, timeout=10)
    check_html(r.text, "Requests")
except Exception as e:
    print(f"Requests failed: {e}")

# 2. Curl with expanded headers
print("\n--- Testing Curl ---")
cmd = [
    'curl', '-L', '-s',
    '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    '-H', 'Accept-Language: en-US,en;q=0.9',
    '-H', 'Referer: https://www.google.com/',
    url
]
try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    check_html(result.stdout, "Curl")
except Exception as e:
    print(f"Curl failed: {e}")
