import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env.local')
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)

# Check for MoFu pages
print("Checking for MoFu pages in database...")
res = supabase.table('pages').select('*').eq('funnel_stage', 'MoFu').execute()

print(f"\nFound {len(res.data)} MoFu pages:")
for page in res.data[:5]:  # Show first 5
    print(f"  - {page.get('topic_title', 'No Title')} (ID: {page['id'][:8]}...)")
    print(f"    Project ID: {page.get('project_id', 'N/A')}")
    print(f"    Page Type: {page.get('page_type', 'N/A')}")
    print(f"    Funnel Stage: {page.get('funnel_stage', 'N/A')}")
    print()
