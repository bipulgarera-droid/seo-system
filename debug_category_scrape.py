"""
Debug scraping for a specific Category URL
"""
import sys
import os

# Add api directory to path to import functions
sys.path.append(os.path.join(os.getcwd(), 'api'))

# Mock environment variables needed for the import
os.environ['GEMINI_API_KEY'] = "mock" # We'll set the real one below
os.environ['SUPABASE_URL'] = "mock"
os.environ['SUPABASE_KEY'] = "mock"

# Manual .env parsing for real keys
for env_file in ['.env', '.env.local']:
    env_path = f'/Users/bipul/Downloads/seo-saas-brain/{env_file}'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    val = val.strip('"').strip("'")
                    os.environ[key] = val

from index import scrape_page_content

# Test URL
url = "https://www.rhodeskin.com/collections/shop-all"
print(f"Testing scrape for: {url}")

try:
    result = scrape_page_content(url)
    
    if result:
        print("\n✅ Scrape Successful!")
        print(f"Title: {result.get('title')}")
        content = result.get('body_content', '')
        print(f"Content Length: {len(content)}")
        print(f"Content Preview: {content[:200]}...")
        
        if len(content) < 100:
            print("\n⚠ WARNING: Content is very short. Might be blocked or empty.")
    else:
        print("\n❌ Scrape Returned None")
        
    # Save HTML for inspection
    import requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }
    r = requests.get(url, headers=headers)
    with open('debug_scrape.html', 'w') as f:
        f.write(r.text)
    print("\nSaved HTML to debug_scrape.html")

except Exception as e:
    print(f"\n❌ Error during scrape: {e}")
    import traceback
    traceback.print_exc()
