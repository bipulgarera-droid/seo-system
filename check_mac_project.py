import os
from dotenv import load_dotenv
from supabase import create_client, Client

print(f"CWD: {os.getcwd()}")
load_dotenv(os.path.join(os.getcwd(), '.env'))

url = os.environ.get("SUPABASE_URL")
print(f"URL: {url}") # Debug print
key = os.environ.get("SUPABASE_KEY")
if not url:
    print("ERROR: SUPABASE_URL not found in env")
    exit(1)
supabase: Client = create_client(url, key)
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Find M.A.C project
res = supabase.table('projects').select('id, domain').ilike('domain', '%maccosmetics%').execute()
projects = res.data

if not projects:
    print("M.A.C Cosmetics project NOT found.")
else:
    p = projects[0]
    print(f"Found Project: {p['domain']} ({p['id']})")
    
    # Check pages
    pages = supabase.table('pages').select('url').eq('project_id', p['id']).execute().data
    print(f"Page Count: {len(pages)}")
    if len(pages) > 0:
        print("Sample URLs:")
        for page in pages[:5]:
            print(f"- {page['url']}")
    else:
        print("No pages found for this project.")
