import sys
import os

# Add api directory to path
sys.path.append(os.path.join(os.getcwd(), 'api'))

from index import crawl_sitemap

def test_sitemap_crawl():
    domain = "https://in.sugarcosmetics.com" # Known large site
    print(f"Testing sitemap crawl for {domain} with limit 1000...")
    
    # Mock supabase to avoid DB errors (we just want to test the crawling logic)
    # But crawl_sitemap doesn't use supabase directly, it returns a list of dicts.
    # Wait, it takes project_id.
    
    pages = crawl_sitemap(domain, "test-project-id", max_pages=1000)
    
    print(f"Found {len(pages)} pages.")
    
    if len(pages) > 254:
        print("SUCCESS: Found more than 254 pages.")
    else:
        print("FAILURE: Stuck at or below 254 pages.")
        
    # Print first 5 and last 5 to see distribution
    if pages:
        print("First 5:")
        for p in pages[:5]:
            print(f"- {p['url']}")
        print("Last 5:")
        for p in pages[-5:]:
            print(f"- {p['url']}")

if __name__ == "__main__":
    test_sitemap_crawl()
