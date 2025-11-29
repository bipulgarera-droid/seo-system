"""
Quick test to verify Category page Scrape Content functionality.
"""

import os
import requests

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

API_BASE = "http://localhost:3000"
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Testing Category Page Scrape Content")
print("=" * 60)

# Find a Category page
result = supabase.table('pages').select('*').eq('page_type', 'Category').limit(1).execute()

if result.data and len(result.data) > 0:
    category_page = result.data[0]
    print(f"✓ Found Category page: {category_page['url']}")
    category_id = category_page['id']
    
    # Test scrape
    response = requests.post(
        f"{API_BASE}/api/batch-update-pages",
        json={"page_ids": [category_id], "action": "scrape_content"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Category Scrape Content WORKS")
        
        # Verify
        updated = supabase.table('pages').select('tech_audit_data').eq('id', category_id).single().execute()
        if updated.data and updated.data.get('tech_audit_data', {}).get('body_content'):
            print(f"✅ Content verified: {len(updated.data['tech_audit_data']['body_content'])} chars")
        else:
            print("⚠️  Content not found after scrape")
    else:
        print(f"❌ FAILED: {response.text}")
else:
    print("⚠️  No Category pages found. Add one first in URL Classification.")
