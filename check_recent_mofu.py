import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env.local')
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# Get the MOST RECENT MoFu pages
res = supabase.table('pages').select('id, created_at, tech_audit_data, research_data').eq('funnel_stage', 'MoFu').order('created_at', desc=True).limit(5).execute()

print("Most Recent MoFu Pages:\n")
for page in res.data:
    created = page.get('created_at', 'Unknown')
    research_data = page.get('research_data') or {}
    citations = research_data.get('citations', [])
    title = (page.get('tech_audit_data') or {}).get('title', 'No Title')
    
    print(f"Created: {created}")
    print(f"Title: {title[:60]}...")
    print(f"Citations: {len(citations)}")
    if citations:
        print(f"  ✓ HAS CITATIONS (Perplexity used!)")
        print(f"  Sample: {str(citations[0])[:100]}...")
    else:
        print("  ✗ NO CITATIONS (Perplexity NOT used)")
    print()
