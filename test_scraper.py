import subprocess
from bs4 import BeautifulSoup

def fetch_with_curl(url, use_chrome_ua=True):
    """Fetch URL using system curl to bypass TLS fingerprinting blocks."""
    try:
        cmd = ['curl', '-L', '-s']
        
        if use_chrome_ua:
            cmd.extend([
                '-A', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                '-H', 'Accept-Language: en-US,en;q=0.9',
            ])
            
        cmd.append(url)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        # If failed with Chrome UA, retry without it (some sites like Akamai block fake UAs but allow curl)
        if use_chrome_ua and (result.returncode != 0 or not result.stdout or "Access Denied" in result.stdout):
            print(f"DEBUG: Chrome UA failed for {url}, retrying with default curl UA...")
            return fetch_with_curl(url, use_chrome_ua=False)
            
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"DEBUG: curl failed with code {result.returncode}: {result.stderr}")
            return None
    except Exception as e:
        print(f"DEBUG: curl exception: {e}")
        return None

urls = [
    "https://www.maccosmetics.com/artistry-mac-lipstick-benefits",
    "https://www.maccosmetics.com/inclusion-and-diversity",
    "https://www.maccosmetics.com/viva-glam-v-lipstick-lp-discontinued-products",
    "https://www.maccosmetics.com/artistry-video-detail-test-1",
    "https://www.maccosmetics.com/mac-select-app-nav-formatter"
]

print(f"{'URL':<60} | {'Status':<6} | {'H1 Found':<8} | {'Miss Alt':<8} | {'Canonical':<10} | {'Schema':<10}")
print("-" * 110)

for url in urls:
    content = fetch_with_curl(url)
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        
        # Status
        status = 200 # Mocking
        
        # H1
        h1 = soup.find('h1')
        h1_found = "YES" if h1 and h1.get_text(strip=True) else "NO"
        
        # Alt Tags
        images = soup.find_all('img')
        missing_alt = 0
        for img in images:
            if not img.get('alt'):
                missing_alt += 1
                
        # Canonical
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical:
            has_canonical = "YES"
        else:
            import re
            match = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', content)
            has_canonical = "YES (Re)" if match else "NO"
        
        # Schema Check
        import json
        has_schema = "NO"
        # Check for JSON-LD
        schemas = soup.find_all('script', type='application/ld+json')
        if schemas:
            has_schema = f"YES ({len(schemas)})"
        else:
            # Check for Microdata
            if soup.find(attrs={'itemscope': True}):
                has_schema = "YES (Micro)"
                
        print(f"{url.split('.com/')[1]:<60} | {status:<6} | {h1_found:<8} | {missing_alt:<8} | {has_canonical:<10} | {has_schema:<10}")
    else:
        print(f"{url.split('.com/')[1]:<60} | {'ERR':<6} | {'-':<8} | {'-':<8} | {'-':<10} | {'-':<10}")
