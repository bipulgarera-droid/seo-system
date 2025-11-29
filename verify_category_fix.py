"""
Verify classify_page logic for Category pages
"""

import os
import requests
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

TEST_DOMAIN = "test-verification-v2.com"

def run_test():
    print("🚀 Testing Category Classification Logic...")
    
    # 1. Create Mock Project & Page
    print("\n1. Creating Mock Data...")
    proj_res = supabase.table('projects').insert({
        "domain": TEST_DOMAIN,
        "project_name": "Test Project V2"
    }).execute()
    pid = proj_res.data[0]['id']
    
    page_res = supabase.table('pages').insert({
        "project_id": pid,
        "url": f"https://{TEST_DOMAIN}/collections/summer-skincare-routine",
        "page_type": None,
        "tech_audit_data": {"title": "Pending Scan"} # Simulate bad initial state
    }).execute()
    page_id = page_res.data[0]['id']
    print(f"   ✓ Created page with title: 'Pending Scan'")

    # 2. Call classify_page API
    print("\n2. Calling classify_page API...")
    # We need to use requests to hit the local API
    try:
        response = requests.post('http://localhost:3000/api/classify-page', json={
            "page_id": page_id,
            "stage": "Category"
        })
        
        if response.status_code == 200:
            print("   ✓ API Call Success")
        else:
            print(f"   ❌ API Call Failed: {response.text}")
            return
            
        # 3. Verify DB Update
        print("\n3. Verifying DB Update...")
        updated_page = supabase.table('pages').select('*').eq('id', page_id).single().execute()
        new_title = updated_page.data.get('tech_audit_data', {}).get('title')
        print(f"   New Title: {new_title}")
        
        if new_title == "Summer Skincare Routine":
            print("   ✅ SUCCESS: Title updated correctly from slug!")
        else:
            print(f"   ❌ FAILURE: Title is '{new_title}' (Expected 'Summer Skincare Routine')")
            
    except Exception as e:
        print(f"   ❌ Error calling API: {e}")
        print("   (Make sure server is running on localhost:3000)")

    # Cleanup
    print("\n4. Cleanup...")
    supabase.table('pages').delete().eq('project_id', pid).execute()
    supabase.table('projects').delete().eq('id', pid).execute()
    print("   ✓ Cleaned up")

if __name__ == "__main__":
    run_test()
