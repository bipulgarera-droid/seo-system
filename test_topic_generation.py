import requests
import os
import json
import time
from supabase import create_client, Client

# Manual .env parsing
for env_file in ['.env', '.env.local']:
    env_path = f'/Users/bipul/Downloads/seo-saas-brain/{env_file}'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    val = val.strip('"').strip("'")
                    os.environ[key] = val

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
API_URL = "http://localhost:3000/api"

if not SUPABASE_URL:
    print("❌ Error: SUPABASE_URL not found.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def log(msg):
    print(f"[TEST] {msg}")

def test_topic_generation():
    # 1. Find a Product Page
    log("Finding a Product page...")
    # Get a product that doesn't have too many MoFu pages yet, or just any product
    res = supabase.table('pages').select('id, url, tech_audit_data').eq('page_type', 'Product').limit(1).execute()
    if not res.data:
        log("❌ No Product pages found.")
        return

    product_page = res.data[0]
    product_id = product_page['id']
    product_title = product_page.get('tech_audit_data', {}).get('title', 'Unknown Product')
    log(f"Found Product: {product_title} ({product_id})")

    # 2. Trigger 'generate_mofu'
    log("Triggering 'generate_mofu' (This should use Gemini Fallback if DataForSEO fails)...")
    try:
        resp = requests.post(f"{API_URL}/batch-update-pages", json={
            "page_ids": [product_id],
            "action": "generate_mofu"
        })
        log(f"Generate MoFu Response: {resp.status_code} - {resp.text}")
    except Exception as e:
        log(f"❌ API Call Failed: {e}")
        return

    # Wait for generation
    log("Waiting for topic generation (approx 30s)...")
    time.sleep(30)

    # 3. Verify Generated Topics
    log("Verifying generated MoFu topics...")
    # Fetch recent MoFu pages for this product
    mofu_res = supabase.table('pages').select('*').eq('source_page_id', product_id).eq('funnel_stage', 'MoFu').order('created_at', desc=True).limit(5).execute()
    
    if not mofu_res.data:
        log("❌ No MoFu pages created. Generation failed.")
        return

    log(f"Found {len(mofu_res.data)} new MoFu topics.")
    
    for page in mofu_res.data:
        title = page.get('tech_audit_data', {}).get('title', 'Untitled')
        keywords_str = page.get('keywords', '')
        
        log(f"\nTopic: {title}")
        
        # Check if we have keywords
        if keywords_str and len(keywords_str) > 50:
            # Count roughly how many keywords
            kw_count = keywords_str.count(',') + 1
            log(f"✅ Keywords Present: Yes (~{kw_count} keywords)")
            log(f"   Sample: {keywords_str[:100]}...")
            
            # If fallback worked, we expect multiple keywords, not just the product title
            if kw_count > 5:
                log("   🌟 SUCCESS: Fallback logic likely worked (Multiple keywords found).")
            else:
                log("   ⚠️ WARNING: Few keywords found. Fallback might have failed or returned minimal data.")
        else:
            log("❌ Keywords Missing or Empty.")

if __name__ == "__main__":
    test_topic_generation()
