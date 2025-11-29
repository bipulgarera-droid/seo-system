"""
Quick test to check if URLs were actually crawled and saved to database.
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

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Find the project with domain 'modeskin.com'
print("Checking for crawled URLs...")
print("=" * 60)

# Get the project
project_result = supabase.table('projects').select('*').eq('domain', 'https://www.modeskin.com/').execute()

if not project_result.data:
    # Try without https://
    project_result = supabase.table('projects').select('*').ilike('domain', '%modeskin.com%').execute()

if project_result.data:
    project = project_result.data[0]
    project_id = project['id']
    print(f"✓ Found project: {project['company_name']}")
    print(f"  Domain: {project['domain']}")
    print(f"  Project ID: {project_id}")
    
    # Count pages for this project
    pages_result = supabase.table('pages').select('*', count='exact').eq('project_id', project_id).execute()
    
    print(f"\n📊 Total pages in database: {pages_result.count}")
    
    if pages_result.count > 0:
        print(f"\n✅ URLs ARE in the database!")
        print("\nSample pages:")
        for page in pages_result.data[:5]:
            print(f"  - {page['url']} (Type: {page.get('page_type', 'Unclassified')})")
        
        # Check classification status
        unclassified = supabase.table('pages').select('*', count='exact').eq('project_id', project_id).is_('page_type', 'null').execute()
        classified = pages_result.count - (unclassified.count or 0)
        
        print(f"\n📈 Classification Status:")
        print(f"  Classified: {classified}")
        print(f"  Unclassified: {unclassified.count or 0}")
    else:
        print("\n❌ No pages found in database!")
        print("   The scrape might have failed or URLs weren't saved.")
else:
    print("❌ Project not found with domain 'modeskin.com'!")
    print("\nAvailable projects:")
    all_projects = supabase.table('projects').select('*').execute()
    for p in all_projects.data:
        name = p.get('company_name') or p.get('name') or p.get('domain') or 'Unknown'
        domain = p.get('domain') or 'No domain'
        print(f"  - {name}: {domain}")
