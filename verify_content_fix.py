"""
Verify Content Generation & Internal Linking Fix
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

TEST_DOMAIN = "test-content-fix.com"

def run_test():
    print("🚀 Starting Content Generation & Linking Verification...")
    
    # 1. Setup Project
    print("\n1. Setting up Project...")
    proj_res = supabase.table('projects').insert({
        "domain": TEST_DOMAIN,
        "project_name": "Content Fix Test"
    }).execute()
    pid = proj_res.data[0]['id']
    print(f"   ✓ Project created: {pid}")

    try:
        # 2. Create Hierarchy
        print("\n2. Creating Page Hierarchy...")
        
        # Product Page
        prod_res = supabase.table('pages').insert({
            "project_id": pid,
            "url": "https://www.rhodeskin.com/products/peptide-lip-treatment",
            "page_type": "Product",
            # "funnel_stage": "Bottom", # Removed to avoid constraint error
            "tech_audit_data": {"title": "Peptide Lip Treatment"}
        }).execute()
        prod_id = prod_res.data[0]['id']
        print(f"   ✓ Product Page: {prod_id}")
        
        # MoFu Page
        mofu_res = supabase.table('pages').insert({
            "project_id": pid,
            "source_page_id": prod_id,
            "url": "https://www.rhodeskin.com/pages/best-lip-treatments",
            "page_type": "Topic",
            "funnel_stage": "MoFu",
            "tech_audit_data": {"title": "Best Lip Treatments 2024"},
            "research_data": {
                "primary_keyword": "best lip treatment",
                "keyword_cluster": [{"keyword": "best lip treatment", "volume": 1000}],
                "perplexity_research": "Research about lip treatments..."
            }
        }).execute()
        mofu_id = mofu_res.data[0]['id']
        print(f"   ✓ MoFu Page: {mofu_id}")
        
        # ToFu Page
        tofu_res = supabase.table('pages').insert({
            "project_id": pid,
            "source_page_id": mofu_id,
            "url": "https://www.rhodeskin.com/pages/why-lips-chapped",
            "page_type": "Topic",
            "funnel_stage": "ToFu",
            "tech_audit_data": {"title": "Why Are My Lips Always Chapped?"},
            "research_data": {
                "primary_keyword": "chapped lips causes",
                "keyword_cluster": [{"keyword": "chapped lips", "volume": 5000}],
                "perplexity_research": "Research about chapped lips..."
            }
        }).execute()
        tofu_id = tofu_res.data[0]['id']
        print(f"   ✓ ToFu Page: {tofu_id}")

        # 3. Test MoFu Generation
        print("\n3. Testing MoFu Content Generation...")
        res = requests.post(f"{API_BASE}/api/batch-update-pages", json={
            "page_ids": [mofu_id],
            "action": "generate_content"
        }, timeout=60)
        
        if res.status_code == 200:
            print("   ✓ MoFu Generation API Success")
            # Verify Content
            page = supabase.table('pages').select('content').eq('id', mofu_id).single().execute()
            content = page.data.get('content', '')
            if content and len(content) > 100:
                print(f"   ✓ Content generated ({len(content)} chars)")
                # Check for Product Link
                if "products/peptide-lip-treatment" in content:
                    print("   ✅ Link to Product found!")
                else:
                    print("   ❌ Link to Product MISSING")
            else:
                print("   ❌ No content generated")
        else:
            print(f"   ❌ API Failed: {res.text}")

        # 4. Test ToFu Generation
        print("\n4. Testing ToFu Content Generation...")
        res = requests.post(f"{API_BASE}/api/batch-update-pages", json={
            "page_ids": [tofu_id],
            "action": "generate_content"
        }, timeout=60)
        
        if res.status_code == 200:
            print("   ✓ ToFu Generation API Success")
            # Verify Content
            page = supabase.table('pages').select('content').eq('id', tofu_id).single().execute()
            content = page.data.get('content', '')
            if content and len(content) > 100:
                print(f"   ✓ Content generated ({len(content)} chars)")
                # Check for MoFu Link
                mofu_link = "pages/best-lip-treatments" in content
                # Check for Product Link
                prod_link = "products/peptide-lip-treatment" in content
                
                if mofu_link: print("   ✅ Link to MoFu found!")
                else: print("   ❌ Link to MoFu MISSING")
                
                if prod_link: print("   ✅ Link to Product (Grandparent) found!")
                else: print("   ❌ Link to Product (Grandparent) MISSING")
            else:
                print("   ❌ No content generated")
        else:
            print(f"   ❌ API Failed: {res.text}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

    # Cleanup
    print("\n5. Cleanup...")
    supabase.table('pages').delete().eq('project_id', pid).execute()
    supabase.table('projects').delete().eq('id', pid).execute()
    print("   ✓ Cleaned up")

if __name__ == "__main__":
    run_test()
