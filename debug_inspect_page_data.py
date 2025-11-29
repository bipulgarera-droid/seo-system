
import os
import json
from supabase import create_client

# Manual .env parsing
for env_file in ['.env', '.env.local']:
    env_path = f'/Users/bipul/Downloads/seo-saas-brain/{env_file}'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    val = val.strip('"').strip("'")
                    os.environ[key] = val

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def inspect_page():
    print("🔍 Searching for 'Tipsy Lips' page...")
    
    # Search for the page
    res = supabase.table('pages').select('*').ilike('tech_audit_data->>title', '%Tipsy Lips%').execute()
    
    if not res.data:
        print("❌ No page found with 'Tipsy Lips' in title.")
        # Try searching for Pinacolada
        res = supabase.table('pages').select('*').ilike('tech_audit_data->>title', '%Pinacolada%').execute()
        
    if not res.data:
        print("❌ No page found with 'Pinacolada' in title.")
        return

    page = res.data[0]
    title = page['tech_audit_data'].get('title')
    print(f"✓ Found Page: {title} ({page['id']})")
    
    r_data = page.get('research_data') or {}
    
    print("\n--- Competitor URLs ---")
    urls = r_data.get('competitor_urls', [])
    for u in urls:
        print(f"- {u}")
        
    print("\n--- Ranked Keywords (Top 10) ---")
    kws = r_data.get('ranked_keywords', [])
    for k in kws[:10]:
        print(f"- {k.get('keyword')} ({k.get('intent')})")
        
    print("\n--- Perplexity Research Preview ---")
    brief = r_data.get('perplexity_research', '')
    print(brief[:500])

if __name__ == "__main__":
    inspect_page()
