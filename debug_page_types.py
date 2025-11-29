"""
Debug: Check what page_type values rhodeskin pages actually have
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

# Get rhodeskin project ID
project = supabase.table('projects').select('*').ilike('domain', '%rhodeskin%').single().execute()
project_id = project.data['id']

# Get pages with project_id and page_type
pages = supabase.table('pages').select('project_id, page_type').eq('project_id', project_id).execute()

print(f"Rhodeskin Project ID: {project_id}")
print(f"Total pages: {len(pages.data)}")
print("\nFirst 10 pages:")
for i, page in enumerate(pages.data[:10], 1):
    print(f"{i}. project_id: {page.get('project_id')}, page_type: {repr(page.get('page_type'))}")

# Count by type
from collections import Counter
types = Counter(page.get('page_type') for page in pages.data)
print(f"\nPage type distribution:")
for page_type, count in types.items():
    print(f"  {repr(page_type)}: {count}")
