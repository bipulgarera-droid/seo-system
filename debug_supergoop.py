import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# Get supergoop project
projects = supabase.table('projects').select('*').ilike('domain', '%supergoop%').execute()

if projects.data:
    project = projects.data[0]
    print(f"Project: {project['project_name']} ({project['domain']})")
    print(f"Project ID: {project['id']}")
    
    # Count pages
    pages = supabase.table('pages').select('*', count='exact').eq('project_id', project['id']).execute()
    print(f"Page count in DB: {pages.count}")
    print(f"\nFirst 5 pages:")
    for page in pages.data[:5]:
        print(f"  - {page['url']}")
else:
    print("Supergoop project not found!")
