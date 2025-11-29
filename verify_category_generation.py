"""
Verify Category Content Generation (Polish Strategy)
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

TEST_DOMAIN = "test-category-polish.com"

def run_test():
    print("🚀 Starting Category Generation Verification (Polish Strategy)...")
    
    # 1. Setup Project
    print("\n1. Setting up Project...")
    proj_res = supabase.table('projects').insert({
        "domain": TEST_DOMAIN,
        "project_name": "Category Polish Test"
    }).execute()
    pid = proj_res.data[0]['id']
    print(f"   ✓ Project created: {pid}")

    # 2. Create Category Page with Short Content
    print("\n2. Creating Category Page...")
    cat_url = "https://www.rhodeskin.com/collections/shop-all"
    initial_content = "Shop the full collection of Rhode Skin products. Glazing fluid, lip treatments, and more. Clean, vegan, cruelty-free."
    
    cat_res = supabase.table('pages').insert({
        "project_id": pid,
        "url": cat_url,
        "page_type": "Category",
        "product_action": "Idle",
        "tech_audit_data": {
            "title": "Shop All - Rhode Skin", 
            "body_content": initial_content
        }
    }).execute()
    cat_id = cat_res.data[0]['id']
    print(f"   ✓ Category Page Created: {cat_id}")

    # 3. Trigger Generate Content
    print("   ⏳ Calling /api/batch-update-pages (action='generate_content')...")
    
    try:
        res = requests.post(f"{API_BASE}/api/batch-update-pages", json={
            "page_ids": [cat_id],
            "action": "generate_content"
        })
        
        if res.status_code == 200:
            print("   ✓ API Call Success")
        else:
            print(f"   ❌ API Call Failed: {res.text}")
            
        # Verify Content
        updated_cat = supabase.table('pages').select('*').eq('id', cat_id).single().execute()
        new_content = updated_cat.data.get('content')
        tech_data = updated_cat.data.get('tech_audit_data') or {}
        meta_desc = tech_data.get('meta_description')
        
        print(f"\n   --- Generated Content Preview ---")
        print(new_content[:500] + "..." if new_content else "None")
        print(f"   ---------------------------------")
        
        length = len(new_content) if new_content else 0
        print(f"   Length: {length} chars")
        print(f"   Meta Description: {meta_desc}")
        
        if length > 0 and length < 3000: # Should be concise, not massive
            print("   ✅ Content generated and length is reasonable (Polish Strategy working)")
        elif length >= 3000:
            print("   ⚠ Content is very long. Check if prompt is still forcing comprehensive guide.")
        else:
            print("   ❌ No content generated")
            
    except Exception as e:
        print(f"   ❌ Error calling API: {e}")

    # Cleanup
    print("\n4. Cleanup...")
    supabase.table('pages').delete().eq('project_id', pid).execute()
    supabase.table('projects').delete().eq('id', pid).execute()
    print("   ✓ Cleaned up")

if __name__ == "__main__":
    run_test()
