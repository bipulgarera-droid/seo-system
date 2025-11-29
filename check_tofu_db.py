
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

def check_results():
    print("🔍 Checking DB for ToFu results...")
    
    # Find the dummy MoFu page
    mofu_url = "https://example.com/mofu-test-arch"
    mofu_res = supabase.table('pages').select('id').eq('url', mofu_url).single().execute()
    
    if not mofu_res.data:
        print("❌ MoFu page not found (maybe deleted?)")
        return
        
    mofu_id = mofu_res.data['id']
    print(f"   ✓ Found MoFu Page: {mofu_id}")
    
    # Find ToFu children
    tofu_pages = supabase.table('pages').select('*').eq('source_page_id', mofu_id).eq('funnel_stage', 'ToFu').execute()
    
    if tofu_pages.data:
        print(f"   ✅ Found {len(tofu_pages.data)} ToFu pages")
        for p in tofu_pages.data:
            title = p['tech_audit_data'].get('title')
            keywords = p.get('keywords', '')
            r_data = p.get('research_data') or {}
            
            print(f"     - Title: {title}")
            
            # Check Keywords Format
            if '|' in keywords:
                print("       ✓ Keywords Format: Standardized (Pipe-separated)")
            else:
                print(f"       ❌ Keywords Format: Invalid ({keywords[:50]}...)")
                
            # Check Auto-Research Data
            if r_data.get('stage') == 'keywords_only' and r_data.get('ranked_keywords'):
                print(f"       ✓ Auto-Research: Success ({len(r_data['ranked_keywords'])} keywords found)")
            else:
                print("       ❌ Auto-Research: Missing or Failed (Background process might still be running)")
                
    else:
        print("   ❌ No ToFu pages found yet.")

if __name__ == "__main__":
    check_results()
