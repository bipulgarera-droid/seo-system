"""
Verify MoFu Generation (Gemini Primary)
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

TEST_DOMAIN = "test-gemini-keywords.com"

def run_test():
    print("🚀 Starting MoFu Generation Verification (Gemini Primary)...")
    
    # 1. Setup Project
    print("\n1. Setting up Project...")
    proj_res = supabase.table('projects').insert({
        "domain": TEST_DOMAIN,
        "project_name": "Gemini Keyword Test"
    }).execute()
    pid = proj_res.data[0]['id']
    print(f"   ✓ Project created: {pid}")

    # 2. Create Product Page
    print("\n2. Creating Product Page...")
    prod_url = "https://www.rhodeskin.com/products/peptide-glazing-fluid"
    prod_res = supabase.table('pages').insert({
        "project_id": pid,
        "url": prod_url,
        "page_type": "Product",
        "product_action": "Idle",
        "tech_audit_data": {"title": "Peptide Glazing Fluid", "body_content": "A lightweight, quick-absorbing, gel-serum that visibly plumps and hydrates to support a healthy skin barrier."}
    }).execute()
    prod_id = prod_res.data[0]['id']
    print(f"   ✓ Product Page Created: {prod_id}")

    # 3. Trigger Generate MoFu
    print("   ⏳ Calling /api/batch-update-pages (action='generate_mofu')...")
    
    try:
        res = requests.post(f"{API_BASE}/api/batch-update-pages", json={
            "page_ids": [prod_id],
            "action": "generate_mofu"
        })
        
        if res.status_code == 200:
            print("   ✓ API Call Success")
        else:
            print(f"   ❌ API Call Failed: {res.text}")
            
        # Verify MoFu Pages Created
        time.sleep(5) # Wait for generation
        mofu_pages = supabase.table('pages').select('*').eq('source_page_id', prod_id).eq('funnel_stage', 'MoFu').execute()
        
        if mofu_pages.data:
            print(f"   ✅ Created {len(mofu_pages.data)} MoFu pages")
            
            # Check keywords in the first page
            first_page = mofu_pages.data[0]
            research_data = first_page.get('research_data') or {}
            keywords = research_data.get('keywords', []) # Or wherever they are stored
            
            # Note: In generate_mofu, keywords are used to generate topics, but are they stored on the MoFu page?
            # Looking at the code: 
            # topic_research['keyword_cluster'] = keyword_cluster
            # topic_research['primary_keyword'] = primary_kw
            
            # We need to check if the TOPICS were generated using a large list.
            # The code generates 6 topics.
            # Let's check if the topics look relevant.
            
            for p in mofu_pages.data:
                print(f"     - {p['tech_audit_data'].get('title')}")
                
        else:
            print("   ❌ No MoFu pages created")
            
    except Exception as e:
        print(f"   ❌ Error calling API: {e}")

    # Cleanup
    print("\n4. Cleanup...")
    supabase.table('pages').delete().eq('project_id', pid).execute()
    supabase.table('projects').delete().eq('id', pid).execute()
    print("   ✓ Cleaned up")

if __name__ == "__main__":
    run_test()
