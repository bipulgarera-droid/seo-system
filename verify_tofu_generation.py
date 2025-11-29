"""
Verify ToFu Generation Performance
"""
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

TEST_DOMAIN = "test-tofu-perf.com"

def run_test():
    print("🚀 Starting ToFu Generation Performance Test...")
    
    # 1. Setup Project
    print("\n1. Setting up Project...")
    proj_res = supabase.table('projects').insert({
        "domain": TEST_DOMAIN,
        "project_name": "ToFu Perf Test"
    }).execute()
    pid = proj_res.data[0]['id']
    print(f"   ✓ Project created: {pid}")

    # 2. Create MoFu Page (Source)
    print("\n2. Creating MoFu Page...")
    mofu_url = "https://www.rhodeskin.com/pages/mofu-test"
    mofu_res = supabase.table('pages').insert({
        "project_id": pid,
        "url": mofu_url,
        "page_type": "Topic",
        "funnel_stage": "MoFu",
        "product_action": "Idle",
        "tech_audit_data": {"title": "Best Peptide Lip Treatments"}
    }).execute()
    mofu_id = mofu_res.data[0]['id']
    print(f"   ✓ MoFu Page Created: {mofu_id}")

    # 3. Trigger Generate ToFu
    print("   ⏳ Calling /api/batch-update-pages (action='generate_tofu')...")
    start_time = time.time()
    
    try:
        res = requests.post(f"{API_BASE}/api/batch-update-pages", json={
            "page_ids": [mofu_id],
            "action": "generate_tofu"
        }, timeout=120) # 2 min timeout
        
        duration = time.time() - start_time
        print(f"   ⏱ API Call Duration: {duration:.2f} seconds")
        
        if res.status_code == 200:
            print("   ✓ API Call Success")
        else:
            print(f"   ❌ API Call Failed: {res.text}")
            
        # Verify ToFu Pages Created
        tofu_pages = supabase.table('pages').select('*').eq('source_page_id', mofu_id).eq('funnel_stage', 'ToFu').execute()
        
        if tofu_pages.data:
            print(f"   ✅ Created {len(tofu_pages.data)} ToFu pages")
            for p in tofu_pages.data:
                print(f"     - {p['tech_audit_data'].get('title')}")
        else:
            print("   ❌ No ToFu pages created")
            
    except Exception as e:
        print(f"   ❌ Error calling API: {e}")

    # Cleanup
    print("\n4. Cleanup...")
    supabase.table('pages').delete().eq('project_id', pid).execute()
    supabase.table('projects').delete().eq('id', pid).execute()
    print("   ✓ Cleaned up")

if __name__ == "__main__":
    run_test()
