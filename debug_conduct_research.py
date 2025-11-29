
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

def run_debug():
    print("🚀 Starting Conduct Research Debugging...")
    
    # 1. Get Existing Project
    print("\n1. Fetching existing project...")
    projects = supabase.table('projects').select('id, project_name').limit(1).execute()
    if not projects.data:
        print("❌ No projects found. Cannot run test.")
        return
    
    project = projects.data[0]
    pid = project['id']
    print(f"   ✓ Using Project: {project['project_name']} ({pid})")

    # 2. Create Dummy MoFu Page (Topic)
    print("\n2. Creating Dummy MoFu Page...")
    mofu_url = "https://example.com/debug-research-test"
    # Clean up any previous run
    supabase.table('pages').delete().eq('url', mofu_url).execute()
    
    mofu_res = supabase.table('pages').insert({
        "project_id": pid,
        "url": mofu_url,
        "page_type": "Topic",
        "funnel_stage": "MoFu",
        "product_action": "Idle",
        "tech_audit_data": {"title": "Debug Research Test Topic"}
    }).execute()
    
    if not mofu_res.data:
        print("❌ Failed to create MoFu page")
        return
        
    mofu_id = mofu_res.data[0]['id']
    print(f"   ✓ MoFu Page Created: {mofu_id}")

    # 3. Trigger Conduct Research
    print("   ⏳ Calling /api/batch-update-pages (action='conduct_research')...")
    start_time = time.time()
    
    try:
        res = requests.post(f"{API_BASE}/api/batch-update-pages", json={
            "page_ids": [mofu_id],
            "action": "conduct_research"
        }, timeout=300) 
        
        duration = time.time() - start_time
        print(f"   ⏱ API Call Duration: {duration:.2f} seconds")
        
        if res.status_code == 200:
            print("   ✓ API Call Success")
        else:
            print(f"   ❌ API Call Failed: {res.text}")
            
        # 4. Verify Research Data
        print("\n4. Verifying Research Output...")
        page = supabase.table('pages').select('*').eq('id', mofu_id).single().execute()
        
        if page.data:
            p = page.data
            r_data = p.get('research_data') or {}
            
            print(f"     - Title: {p['tech_audit_data'].get('title')}")
            
            if r_data.get('perplexity_research'):
                print("       ✓ Perplexity Research: Found")
                print(f"       Preview: {r_data['perplexity_research'][:100]}...")
            else:
                print("       ❌ Perplexity Research: Missing")
                
            if r_data.get('ranked_keywords'):
                print(f"       ✓ Keywords: Found ({len(r_data['ranked_keywords'])})")
            else:
                print("       ❌ Keywords: Missing")
                
    except Exception as e:
        print(f"   ❌ Error calling API: {e}")

    # Cleanup
    print("\n5. Cleanup...")
    supabase.table('pages').delete().eq('id', mofu_id).execute()
    print("   ✓ Cleaned up dummy page")

if __name__ == "__main__":
    run_debug()
