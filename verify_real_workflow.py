"""
Verify Real Workflow (API Simulation)
Simulates the frontend API calls to verify Category Scraping and MoFu Research.
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

TEST_DOMAIN = "test-real-workflow-v1.com"

def run_test():
    print("🚀 Starting Real Workflow Verification (API Simulation)...")
    
    # 1. Setup Project
    print("\n1. Setting up Project...")
    proj_res = supabase.table('projects').insert({
        "domain": TEST_DOMAIN,
        "project_name": "Real Workflow Test"
    }).execute()
    pid = proj_res.data[0]['id']
    print(f"   ✓ Project created: {pid}")

    # ---------------------------------------------------------
    # TEST 1: CATEGORY SCRAPING
    # ---------------------------------------------------------
    print("\n2. Testing Category Scraping (API)...")
    cat_url = "https://www.rhodeskin.com/collections/shop-all"
    cat_res = supabase.table('pages').insert({
        "project_id": pid,
        "url": cat_url,
        "page_type": "Category",
        "product_action": "Idle"
    }).execute()
    cat_id = cat_res.data[0]['id']
    
    print(f"   ✓ Category Page Created: {cat_id}")
    print("   ⏳ Calling /api/batch-update-pages (action='scrape_content')...")
    
    try:
        res = requests.post(f"{API_BASE}/api/batch-update-pages", json={
            "page_ids": [cat_id],
            "action": "scrape_content"
        })
        
        if res.status_code == 200:
            print("   ✓ API Call Success")
        else:
            print(f"   ❌ API Call Failed: {res.text}")
            
        # Verify DB
        time.sleep(2) # Give it a moment if async (though it's sync in code)
        updated_cat = supabase.table('pages').select('*').eq('id', cat_id).single().execute()
        tech_data = updated_cat.data.get('tech_audit_data') or {}
        
        title = tech_data.get('title')
        body = tech_data.get('body_content')
        
        print(f"   Title: {title}")
        print(f"   Body Length: {len(body) if body else 0}")
        
        if title and body and len(body) > 100:
            print("   ✅ Category Scraping Verified!")
        else:
            print("   ❌ Category Scraping Failed (Missing Title or Body)")
            
    except Exception as e:
        print(f"   ❌ Error calling API: {e}")

    # ---------------------------------------------------------
    # TEST 2: MOFU RESEARCH
    # ---------------------------------------------------------
    print("\n3. Testing MoFu Research (API)...")
    # Create a MoFu page with some keywords to trigger research
    mofu_res = supabase.table('pages').insert({
        "project_id": pid,
        "url": f"https://{TEST_DOMAIN}/blog/best-skincare-routine",
        "page_type": "Topic",
        "funnel_stage": "MoFu",
        "product_action": "Idle",
        "tech_audit_data": {"title": "Best Skincare Routine for 2025"},
        "research_data": {
            "ranked_keywords": [{"keyword": "best skincare routine", "intent": "commercial"}]
        }
    }).execute()
    mofu_id = mofu_res.data[0]['id']
    
    print(f"   ✓ MoFu Page Created: {mofu_id}")
    print("   ⏳ Calling /api/batch-update-pages (action='conduct_research')...")
    
    try:
        res = requests.post(f"{API_BASE}/api/batch-update-pages", json={
            "page_ids": [mofu_id],
            "action": "conduct_research"
        })
        
        if res.status_code == 200:
            print("   ✓ API Call Success")
        else:
            print(f"   ❌ API Call Failed: {res.text}")
            
        # Verify DB
        updated_mofu = supabase.table('pages').select('*').eq('id', mofu_id).single().execute()
        r_data = updated_mofu.data.get('research_data') or {}
        
        perp_res = r_data.get('perplexity_research')
        citations = r_data.get('citations')
        
        print(f"   Research Length: {len(perp_res) if perp_res else 0}")
        print(f"   Citations: {len(citations) if citations else 0}")
        
        if perp_res and len(perp_res) > 100:
            print("   ✅ MoFu Research Verified!")
        else:
            print("   ❌ MoFu Research Failed (No Research Data)")
            
    except Exception as e:
        print(f"   ❌ Error calling API: {e}")

    # Cleanup
    print("\n4. Cleanup...")
    supabase.table('pages').delete().eq('project_id', pid).execute()
    supabase.table('projects').delete().eq('id', pid).execute()
    print("   ✓ Cleaned up")

if __name__ == "__main__":
    run_test()
