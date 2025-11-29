
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
    print("🚀 Starting ToFu Architecture Verification...")
    
    # 1. Get Existing Project
    print("\n1. Fetching existing project...")
    projects = supabase.table('projects').select('id, project_name').limit(1).execute()
    if not projects.data:
        print("❌ No projects found. Cannot run test.")
        return
    
    project = projects.data[0]
    pid = project['id']
    print(f"   ✓ Using Project: {project['project_name']} ({pid})")

    # 2. Create Dummy MoFu Page
    print("\n2. Creating Dummy MoFu Page...")
    mofu_url = "https://example.com/mofu-test-arch"
    # Clean up any previous run
    supabase.table('pages').delete().eq('url', mofu_url).execute()
    
    mofu_res = supabase.table('pages').insert({
        "project_id": pid,
        "url": mofu_url,
        "page_type": "Topic",
        "funnel_stage": "MoFu",
        "product_action": "Idle",
        "tech_audit_data": {"title": "Best Eco-Friendly Lip Balms 2025"}
    }).execute()
    
    if not mofu_res.data:
        print("❌ Failed to create MoFu page")
        return
        
    mofu_id = mofu_res.data[0]['id']
    print(f"   ✓ MoFu Page Created: {mofu_id}")

    # 3. Trigger Generate ToFu
    print("   ⏳ Calling /api/batch-update-pages (action='generate_tofu')...")
    start_time = time.time()
    
    try:
        res = requests.post(f"{API_BASE}/api/batch-update-pages", json={
            "page_ids": [mofu_id],
            "action": "generate_tofu"
        }, timeout=300) # Long timeout for research (5 topics * 20s = 100s+)
        
        duration = time.time() - start_time
        print(f"   ⏱ API Call Duration: {duration:.2f} seconds")
        
        if res.status_code == 200:
            print("   ✓ API Call Success")
        else:
            print(f"   ❌ API Call Failed: {res.text}")
            
        # 4. Verify ToFu Pages & Research Data
        print("\n4. Verifying ToFu Output...")
        tofu_pages = supabase.table('pages').select('*').eq('source_page_id', mofu_id).eq('funnel_stage', 'ToFu').execute()
        
        if tofu_pages.data:
            print(f"   ✅ Created {len(tofu_pages.data)} ToFu pages")
            for p in tofu_pages.data:
                title = p['tech_audit_data'].get('title')
                keywords = p.get('keywords', '')
                r_data = p.get('research_data') or {}
                
                print(f"     - Title: {title}")
                
                # Check Keywords Format
                if '|' in keywords:
                    print("       ✓ Keywords Format: Standardized (Pipe-separated)")
                else:
                    print(f"       ❌ Keywords Format: Invalid ({keywords[:50]}...)")
                    
                # Check Auto-Research Data
                if r_data.get('stage') == 'keywords_only' and r_data.get('ranked_keywords'):
                    print(f"       ✓ Auto-Research: Success ({len(r_data['ranked_keywords'])} keywords found)")
                else:
                    print("       ❌ Auto-Research: Missing or Failed")
                    
        else:
            print("   ❌ No ToFu pages created")
            
    except Exception as e:
        print(f"   ❌ Error calling API: {e}")

    # Cleanup
    print("\n5. Cleanup...")
    supabase.table('pages').delete().eq('source_page_id', mofu_id).execute() # Delete ToFu
    supabase.table('pages').delete().eq('id', mofu_id).execute() # Delete MoFu
    print("   ✓ Cleaned up dummy pages")

if __name__ == "__main__":
    run_test()
