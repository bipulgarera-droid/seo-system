
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

def run_test():
    print("🚀 Starting Crash Verification...")
    
    # 1. Get Existing Project
    projects = supabase.table('projects').select('id').limit(1).execute()
    if not projects.data: return
    pid = projects.data[0]['id']

    # 2. Create Dummy Page WITH Keywords (to trigger the bug)
    print("\n2. Creating Dummy Page WITH Keywords...")
    mofu_url = "https://example.com/crash-test"
    supabase.table('pages').delete().eq('url', mofu_url).execute()
    
    mofu_res = supabase.table('pages').insert({
        "project_id": pid,
        "url": mofu_url,
        "page_type": "Topic",
        "funnel_stage": "MoFu",
        "product_action": "Idle",
        "tech_audit_data": {"title": "Crash Test Topic"},
        "research_data": {
            "ranked_keywords": [{"keyword": "test", "intent": "info"}] # Existing keywords
        }
    }).execute()
    
    mofu_id = mofu_res.data[0]['id']
    print(f"   ✓ Page Created: {mofu_id}")

    # 3. Trigger Conduct Research
    print("   ⏳ Calling /api/batch-update-pages...")
    
    try:
        res = requests.post(f"{API_BASE}/api/batch-update-pages", json={
            "page_ids": [mofu_id],
            "action": "conduct_research"
        }, timeout=30)
        
        if res.status_code == 500:
            print("   ✅ API Returned 500 (Expected Crash)")
            print(f"   Error: {res.text}")
        elif res.status_code == 200:
            print("   ❌ API Returned 200 (Unexpected Success)")
        else:
            print(f"   ❓ API Returned {res.status_code}: {res.text}")
            
    except Exception as e:
        print(f"   ❌ Error calling API: {e}")

    # Cleanup
    supabase.table('pages').delete().eq('id', mofu_id).execute()

if __name__ == "__main__":
    run_test()
