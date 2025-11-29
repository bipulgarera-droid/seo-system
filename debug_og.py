import requests
from bs4 import BeautifulSoup

url = "https://newvisiondigital.in/about-us"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    res = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {res.status_code}")
    soup = BeautifulSoup(res.content, 'html.parser')
    
    og_title = soup.find('meta', property='og:title')
    print(f"OG Title (property): {og_title.get('content') if og_title else 'Not Found'}")
    
    og_desc = soup.find('meta', property='og:description')
    print(f"OG Desc (property): {og_desc.get('content') if og_desc else 'Not Found'}")
    
    # Check for name attribute just in case
    og_title_name = soup.find('meta', attrs={'name': 'og:title'})
    print(f"OG Title (name): {og_title_name.get('content') if og_title_name else 'Not Found'}")

except Exception as e:
    print(f"Error: {e}")
