import os
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv('.env.local')
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# Get ONE MoFu page to inspect its tech_audit_data specifically
res = supabase.table('pages').select('id, url, tech_audit_data, content_description, keywords, slug').eq('funnel_stage', 'MoFu').limit(1).execute()

if res.data:
    page = res.data[0]
    print("MoFu Page Core Fields:")
    print(f"ID: {page['id']}")
    print(f"URL: {page.get('url', 'N/A')}")
    print(f"Slug: {page.get('slug', 'N/A')}")
    print(f"Content Description: {page.get('content_description', 'N/A')[:100]}...")
    print(f"Keywords: {page.get('keywords', 'N/A')[:100]}...")
    print(f"\ntech_audit_data:")
    print(json.dumps(page.get('tech_audit_data'), indent=2))
else:
    print("No MoFu pages found")
