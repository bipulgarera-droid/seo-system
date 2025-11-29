import os
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv('.env.local')
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# Check if MoFu pages have Perplexity citations
res = supabase.table('pages').select('id, created_at, research_data').eq('funnel_stage', 'MoFu').limit(3).execute()

print("Checking if MoFu pages used Perplexity (checking for citations):\n")
for page in res.data:
    created = page.get('created_at', 'Unknown')
    research_data = page.get('research_data') or {}
    citations = research_data.get('citations', [])
    
    print(f"Page ID: {page['id'][:8]}...")
    print(f"Created: {created}")
    print(f"Citations: {len(citations)}")
    if citations:
        print(f"  Sample: {citations[0][:80]}..." if citations[0] else "  Empty citation")
    else:
        print("  ✗ NO CITATIONS (Perplexity not used)")
    print()
