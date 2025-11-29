import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('/Users/bipul/Downloads/seo-saas-brain/.env')

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')

if not url or not key:
    print("Error: Supabase credentials missing in .env")
    exit(1)

supabase = create_client(url, key)

print("--- Checking Page Types ---")
res = supabase.table('pages').select('page_type, funnel_stage').limit(50).execute()

types = set()
stages = set()

for p in res.data:
    types.add(p.get('page_type'))
    stages.add(p.get('funnel_stage'))

print(f"Unique Page Types found: {types}")
print(f"Unique Funnel Stages found: {stages}")

print("\n--- Checking MoFu Topics ---")
mofu_res = supabase.table('pages').select('*').eq('funnel_stage', 'MoFu').execute()
print(f"Number of pages with funnel_stage='MoFu': {len(mofu_res.data)}")
if len(mofu_res.data) == 0:
    # Try lowercase
    mofu_lower = supabase.table('pages').select('*').eq('funnel_stage', 'mofu').execute()
    print(f"Number of pages with funnel_stage='mofu': {len(mofu_lower.data)}")
