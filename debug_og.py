import subprocess
from bs4 import BeautifulSoup

def fetch_with_curl(url):
    try:
        cmd = ['curl', '-L', '-s', 
               '-A', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
               url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return result.stdout
    except Exception as e:
        print(f"Error: {e}")
        return None

url = "https://supergoop.com/products/100-mineral-sunscreen-stick"
print(f"Fetching {url}...")
html = fetch_with_curl(url)

if html:
    soup = BeautifulSoup(html, 'html.parser')
    
    og_title = soup.find('meta', property='og:title')
    print(f"OG Title (property='og:title'): {og_title}")
    
    og_desc = soup.find('meta', property='og:description')
    print(f"OG Desc (property='og:description'): {og_desc}")
    
    # Check for name attribute variant
    og_title_name = soup.find('meta', attrs={'name': 'og:title'})
    print(f"OG Title (name='og:title'): {og_title_name}")

    # Print first 500 chars of head to see what's there
    head = soup.find('head')
    if head:
        print("\nHead content snippet:")
        print(head.decode_contents()[:1000])
else:
    print("Failed to fetch HTML")
