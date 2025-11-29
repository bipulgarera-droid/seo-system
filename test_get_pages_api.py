"""
Test /api/get-pages endpoint for rhodeskin
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

# Get rhodeskin project ID
project = supabase.table('projects').select('*').ilike('domain', '%rhodeskin%').single().execute()
project_id = project.data['id']

print(f"Testing /api/get-pages for rhodeskin...")
print(f"Project ID: {project_id}")
print("=" * 60)

# Test the API endpoint
response = requests.get(f"http://localhost:3000/api/get-pages?project_id={project_id}")

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    pages = data.get('pages', [])
    
    print(f"✅ API Response SUCCESS")
    print(f"📊 Pages returned: {len(pages)}")
    
    if pages:
        print(f"\nFirst 5 pages:")
        for i, page in enumerate(pages[:5], 1):
            print(f"  {i}. {page['url']}")
            print(f"     Type: {page.get('page_type', 'None')}")
            print(f"     Status: {page.get('status', 'Unknown')}")
    else:
        print("\n⚠️  No pages in API response (but 253 are in DB!)")
        print("This means the API is filtering them out somehow.")
else:
    print(f"❌ API Error: {response.status_code}")
    print(response.text)
