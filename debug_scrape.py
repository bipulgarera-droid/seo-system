import requests
from bs4 import BeautifulSoup

url = "https://www.nytarra.in/products/mayakhel-playing-cards"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the unwanted text
        target_text = soup.find(string=lambda text: text and "Positive Vibes" in text)
        
        if target_text:
            print(f"\nFOUND UNWANTED TEXT: '{target_text.strip()[:50]}...'")
            print("PARENT HIERARCHY:")
            parent = target_text.parent
            while parent and parent.name != 'html':
                classes = parent.get('class', [])
                print(f" -> {parent.name} (Classes: {classes})")
                parent = parent.parent
        else:
            print("Unwanted text not found in raw HTML.")

except Exception as e:
    print(f"Error: {e}")
