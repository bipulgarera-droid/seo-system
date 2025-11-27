import requests
from bs4 import BeautifulSoup
import time

url = "https://www.apple.com.cn/shop/buy-mac/imac/Z1ET"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Testing fetch for: {url}")
try:
    start_time = time.time()
    response = requests.get(url, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    print(f"Time: {time.time() - start_time:.2f}s")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"Title: {soup.title.string.strip() if soup.title else 'No Title'}")
        print(f"Content Length: {len(response.content)}")
    else:
        print("Failed to fetch.")
        print(response.text[:500])
        
except Exception as e:
    print(f"Error: {e}")
