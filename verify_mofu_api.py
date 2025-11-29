
import os
import requests
import time
import json
from supabase import create_client

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

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
API_BASE = "http://localhost:3000"

def run_verification():
    print("🚀 Starting MoFu API Verification...")
    
    # 1. Get a Product Page
    print("1. Fetching a Product Page...")
    # Get a product that DOESN'T have MoFu topics yet if possible, or just any product
    res = supabase.table('pages').select('*').eq('page_type', 'Product').limit(1).execute()
    if not res.data:
        print("❌ No Product pages found.")
        return
    
    product = res.data[0]
    pid = product['id']
    p_title = product['tech_audit_data'].get('title', 'Unknown Product')
    print(f"   ✓ Using Product: {p_title} ({pid})")
    
    # 2. Check existing MoFu topics count
    existing_topics = supabase.table('pages').select('id').eq('source_page_id', pid).eq('funnel_stage', 'MoFu').execute()
    initial_count = len(existing_topics.data)
    print(f"   ℹ️ Initial MoFu Topics: {initial_count}")

    # 3. Trigger Generate MoFu
    print("3. Calling /api/batch-update-pages (action='generate_mofu')...")
    start_time = time.time()
    
    try:
        res = requests.post(f"{API_BASE}/api/batch-update-pages", json={
            "page_ids": [pid],
            "action": "generate_mofu"
        }, timeout=120) 
        
        duration = time.time() - start_time
        print(f"   ⏱ API Call Duration: {duration:.2f} seconds")
        
        if res.status_code == 200:
            print("   ✓ API Call Success (200 OK)")
            print(f"   Response: {res.text}")
        else:
            print(f"   ❌ API Call Failed: {res.status_code} - {res.text}")
            return

        # 4. Verify New Topics
        print("4. Verifying Database...")
        new_topics = supabase.table('pages').select('*').eq('source_page_id', pid).eq('funnel_stage', 'MoFu').execute()
        final_count = len(new_topics.data)
        print(f"   ℹ️ Final MoFu Topics: {final_count}")
        
        if final_count > initial_count:
            print(f"   ✅ SUCCESS: Generated {final_count - initial_count} new topics!")
            # Print details of one topic to check structure
            topic = new_topics.data[0]
            print("\n   --- Topic Sample ---")
            print(f"   Title: {topic['tech_audit_data'].get('title')}")
            print(f"   Slug: {topic['slug']}")
            print(f"   Page Type: {topic['page_type']}")
            print(f"   Funnel Stage: {topic['funnel_stage']}")
            print(f"   Source Page ID: {topic['source_page_id']}")
        else:
            print("   ❌ FAILURE: No new topics found in DB.")

    except Exception as e:
        print(f"   ❌ Error calling API: {e}")

if __name__ == "__main__":
    run_verification()
