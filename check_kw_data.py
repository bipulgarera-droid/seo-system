import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env.local')
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# Get the most recent MoFu page and check keywords
res = supabase.table('pages').select('id, tech_audit_data, keywords, research_data').eq('funnel_stage', 'MoFu').order('created_at', desc=True).limit(1).execute()

if res.data:
    page = res.data[0]
    title = (page.get('tech_audit_data') or {}).get('title', 'No Title')
    keywords = page.get('keywords', '')
    research_data = page.get('research_data') or {}
    citations = research_data.get('citations', [])
    
    print(f"Most Recent MoFu Page:")
    print(f"  Title: {title[:60]}...")
    print(f"\nKeywords Field:")
    print(f"  Value: '{keywords[:200] if keywords else 'EMPTY'}'")
    print(f"\nCitations ({len(citations)}):")
    for i, cite in enumerate(citations[:3]):
        print(f"  {i+1}. {str(cite)[:80]}...")
    
    # Check if we have actual keyword data in research_data
    kw_data = research_data.get('keywords', [])
    print(f"\nKeyword Data in research_data: {len(kw_data)} keywords")
    if kw_data:
        print("  Sample:")
        for kw in kw_data[:3]:
            print(f"    - {kw.get('keyword', 'N/A')} (Vol: {kw.get('volume', 0)})")
