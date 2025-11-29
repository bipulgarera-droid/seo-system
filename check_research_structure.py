import os
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv('.env.local')
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# Get ONE recent page and show full research_data structure
res = supabase.table('pages').select('research_data').eq('funnel_stage', 'MoFu').order('created_at', desc=True).limit(1).execute()

if res.data:
    research_data = res.data[0].get('research_data') or {}
    print("Research Data Structure:")
    print(f"  Citations: {research_data.get('citations', [])}")
    print(f"  Keywords count: {len(research_data.get('keywords', []))}")
    print(f"  SERP analysis count: {len(research_data.get('serp_analysis', {}))}")
    print(f"\nPerplexity Research (first 500 chars):")
    print(research_data.get('perplexity_research', 'N/A')[:500])
