"""
Check rhodeskin.com pages in database
"""

import os
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

print("Checking rhodeskin.com...")
print("=" * 60)

# Get rhodeskin project
project = supabase.table('projects').select('*').ilike('domain', '%rhodeskin%').execute()

if project.data:
    proj = project.data[0]
    print(f"✓ Found project: {proj['domain']}")
    print(f"  Project ID: {proj['id']}")
    
    # Get pages
    pages = supabase.table('pages').select('*', count='exact').eq('project_id', proj['id']).execute()
    
    print(f"\n📊 Total pages: {pages.count}")
    
    if pages.count > 0:
        print("\n✅ Pages ARE in database!")
        print(f"\nShowing first 10 pages:")
        for i, page in enumerate(pages.data[:10], 1):
            print(f"  {i}. {page['url']}")
            print(f"     Type: {page.get('page_type', 'Unclassified')}")
            print(f"     Status: {page.get('status', 'Unknown')}")
    else:
        print("\n❌ No pages found!")
        print("The crawl might have failed.")
else:
    print("❌ rhodeskin.com project not found!")
