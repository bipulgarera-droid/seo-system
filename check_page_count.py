"""
Check if page_count field is set in projects table for rhodeskin
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

print("Checking page_count field in projects table...")
print("=" * 60)

# Get rhodeskin project
project = supabase.table('projects').select('*').ilike('domain', '%rhodeskin%').single().execute()

if project.data:
    print(f"Project: {project.data['domain']}")
    print(f"page_count field: {project.data.get('page_count', 'MISSING')}")
    print(f"classified_count field: {project.data.get('classified_count', 'MISSING')}")
    
    # Count actual pages in database
    actual_count = supabase.table('pages').select('*', count='exact').eq('project_id', project.data['id']).execute()
    
    print(f"\n📊 Actual pages in database: {actual_count.count}")
    print(f"📊 page_count field value: {project.data.get('page_count', 0)}")
    
    if project.data.get('page_count', 0) != actual_count.count:
        print(f"\n❌ MISMATCH! page_count field is not being updated correctly.")
        print(f"   Expected: {actual_count.count}")
        print(f"   Got: {project.data.get('page_count', 0)}")
    else:
        print(f"\n✅ page_count is correct!")
else:
    print("❌ Project not found!")
