import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env.local')
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# Get the VERY MOST RECENT page (within last minute)
res = supabase.table('pages').select('id, created_at, research_data').eq('funnel_stage', 'MoFu').order('created_at', desc=True).limit(1).execute()

if res.data:
    page = res.data[0]
    created = page.get('created_at', 'Unknown')
    research_data = page.get('research_data') or {}
    
    print(f"Most Recent MoFu Page:")
    print(f"  Created: {created}")
    print(f"  ID: {page['id']}")
    
    # Check the actual research field
    perplexity_research = research_data.get('perplexity_research', '')
    citations = research_data.get('citations', [])
    
    print(f"\nPerplexity Research (first 200 chars):")
    print(f"  {perplexity_research[:200]}")
    print(f"\nCitations: {citations}")
    
    # Determine if it's really Perplexity or Gemini
    if 'Gemini AI Research' in str(citations):
        print("\n✗ Using GEMINI fallback")
    elif len(citations) > 1:
        print(f"\n✓ Using REAL PERPLEXITY ({len(citations)} citations)")
    else:
        print("\n? Unknown source")
