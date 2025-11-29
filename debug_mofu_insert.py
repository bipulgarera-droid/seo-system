
import os
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

def debug_insert():
    print("🚀 Starting MoFu Insert Debug...")
    
    # 1. Get a Product Page
    res = supabase.table('pages').select('*').eq('page_type', 'Product').limit(1).execute()
    if not res.data:
        print("❌ No Product pages found.")
        return
    product = res.data[0]
    pid = product['id']
    print(f"   ✓ Using Product: {product['tech_audit_data'].get('title')} ({pid})")

    # 2. Prepare Dummy MoFu Topic Data (Exact structure from index.py)
    new_page = {
        "project_id": product['project_id'],
        "source_page_id": pid,
        "url": f"{product['url'].rstrip('/')}/debug-mofu-test",
        "page_type": "Topic",
        "funnel_stage": "MoFu",
        "product_action": "Idle",
        "tech_audit_data": {
            "title": "Debug MoFu Topic",
            "meta_description": "Test description",
            "meta_title": "Debug MoFu Topic"
        },
        "content_description": "Test description",
        "keywords": "test | informational |",
        "slug": "debug-mofu-test",
        "research_data": {
            "notes": "Test notes",
            "keyword_cluster": [{"keyword": "test", "volume": 100}],
            "primary_keyword": "test"
        }
    }
    
    # 3. Attempt Insert
    print("3. Attempting Insert WITH research_data...")
    try:
        insert_res = supabase.table('pages').insert([new_page]).execute()
        print("✅ Insert SUCCESS!")
        print(f"   ID: {insert_res.data[0]['id']}")
        
        # Cleanup
        supabase.table('pages').delete().eq('id', insert_res.data[0]['id']).execute()
        print("   ✓ Cleaned up.")
        
    except Exception as e:
        print(f"❌ Insert FAILED: {e}")
        
        # 4. Retry WITHOUT research_data (Simulate Fallback)
        print("\n4. Retrying WITHOUT research_data...")
        try:
            new_page.pop('research_data')
            insert_res = supabase.table('pages').insert([new_page]).execute()
            print("✅ Fallback Insert SUCCESS!")
            
            # Cleanup
            supabase.table('pages').delete().eq('id', insert_res.data[0]['id']).execute()
            print("   ✓ Cleaned up.")
            
        except Exception as e2:
            print(f"❌ Fallback Insert FAILED: {e2}")

if __name__ == "__main__":
    debug_insert()
