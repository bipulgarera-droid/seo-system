
import sys
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv('.env.local')

# Add current dir to path to import api
sys.path.append(os.getcwd())

from api.index import process_content_generation, supabase

# Fetch a real product page ID to test
print("Fetching a product page to test...")
try:
    # Get a product page that has content (so we don't need to scrape)
    res = supabase.table('pages').select('id, url, tech_audit_data').eq('page_type', 'Product').limit(1).execute()
    if res.data:
        page = res.data[0]
        page_id = page['id']
        print(f"Testing content generation for Page ID: {page_id}")
        print(f"URL: {page['url']}")
        print(f"Title: {page.get('tech_audit_data', {}).get('title')}")
        
        # Run generation synchronously
        print("\n--- Starting Generation ---")
        process_content_generation([page_id], os.environ.get("GEMINI_API_KEY"))
        print("\n--- Generation Complete ---")
        
        # Verify result
        updated_page = supabase.table('pages').select('content, product_action').eq('id', page_id).single().execute()
        print(f"Action Status: {updated_page.data.get('product_action')}")
        print(f"Content Length: {len(updated_page.data.get('content', '') or '')}")
    else:
        print("No product pages found in DB to test.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
