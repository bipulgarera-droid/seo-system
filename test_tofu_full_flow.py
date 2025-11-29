import requests
import os
import json
import time
from supabase import create_client, Client
# Manual .env parsing
for env_file in ['.env', '.env.local']:
    env_path = f'/Users/bipul/Downloads/seo-saas-brain/{env_file}'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    # Remove quotes if present
                    val = val.strip('"').strip("'")
                    os.environ[key] = val

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL:
    print("❌ Error: SUPABASE_URL not found even after manual parsing.")
    exit(1)
API_URL = "http://localhost:3000/api"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def log(msg):
    print(f"[TEST] {msg}")

def test_workflow():
    # 1. Find a MoFu Page
    log("Finding a MoFu page...")
    res = supabase.table('pages').select('id, url, tech_audit_data').eq('funnel_stage', 'MoFu').limit(1).execute()
    if not res.data:
        log("❌ No MoFu pages found. Cannot test ToFu generation.")
        return

    mofu_page = res.data[0]
    mofu_id = mofu_page['id']
    mofu_title = mofu_page.get('tech_audit_data', {}).get('title', 'Unknown')
    log(f"Found MoFu Page: {mofu_title} ({mofu_id})")

    # 2. Generate ToFu Topics
    log("Triggering 'generate_tofu'...")
    try:
        resp = requests.post(f"{API_URL}/batch-update-pages", json={
            "page_ids": [mofu_id],
            "action": "generate_tofu"
        })
        log(f"Generate ToFu Response: {resp.status_code} - {resp.text}")
    except Exception as e:
        log(f"❌ API Call Failed: {e}")
        return

    # Wait for generation (it's async in the backend usually, but here it might be sync or we need to poll)
    # The current implementation in index.py seems synchronous for the generation part, 
    # but let's wait a bit to be sure DB is updated.
    time.sleep(5)

    # 3. Verify ToFu Creation & Auto-Keywords
    log("Verifying ToFu creation and Auto-Keywords...")
    # Fetch ToFu pages linked to this MoFu
    tofu_res = supabase.table('pages').select('*').eq('source_page_id', mofu_id).eq('funnel_stage', 'ToFu').order('created_at', desc=True).limit(5).execute()
    
    if not tofu_res.data:
        log("❌ No ToFu pages created.")
        return

    new_tofu = tofu_res.data[0]
    log(f"Created ToFu Page: {new_tofu.get('tech_audit_data', {}).get('title')} ({new_tofu['id']})")
    
    # Check Keywords
    keywords = new_tofu.get('keywords', '')
    research_data = new_tofu.get('research_data', {})
    
    if keywords and len(keywords) > 10:
        log("✅ Auto-Keywords populated successfully.")
    else:
        log(f"❌ Auto-Keywords missing or empty. Keywords: {keywords}")

    if research_data.get('ranked_keywords'):
        log("✅ Research Data (Keywords) populated.")
    else:
        log("❌ Research Data (Keywords) missing.")

    # 4. Test 'Conduct Research' (Manual Trigger)
    tofu_id = new_tofu['id']
    log(f"Triggering 'conduct_research' for ToFu page {tofu_id}...")
    
    try:
        resp = requests.post(f"{API_URL}/batch-update-pages", json={
            "page_ids": [tofu_id],
            "action": "conduct_research"
        })
        log(f"Conduct Research Response: {resp.status_code}")
    except Exception as e:
        log(f"❌ API Call Failed: {e}")

    # Poll for research completion
    log("Waiting for research to complete (polling)...")
    for i in range(10):
        time.sleep(5)
        page_check = supabase.table('pages').select('research_data').eq('id', tofu_id).single().execute()
        rd = page_check.data.get('research_data', {})
        if rd.get('perplexity_research'):
            log("✅ Perplexity Research completed and saved.")
            break
        log(f"Waiting... ({i+1}/10)")
    else:
        log("❌ Research timed out or failed.")

    # 5. Test 'Generate Content'
    log(f"Triggering 'generate_content' for ToFu page {tofu_id}...")
    try:
        resp = requests.post(f"{API_URL}/batch-update-pages", json={
            "page_ids": [tofu_id],
            "action": "generate_content"
        })
        log(f"Generate Content Response: {resp.status_code}")
    except Exception as e:
        log(f"❌ API Call Failed: {e}")

    # Poll for content
    log("Waiting for content generation...")
    for i in range(15):
        time.sleep(5)
        page_check = supabase.table('pages').select('content').eq('id', tofu_id).single().execute()
        content = page_check.data.get('content', '')
        if content and len(content) > 100:
            log("✅ Content generated successfully.")
            
            # 6. Verify Content Quality (Main Product Link)
            if "Main Product" in content or "product" in content.lower(): # Simple check
                log("✅ Content contains product references.")
            
            # Check for specific link structure if possible, but text varies.
            # We look for the Main Product URL
            mofu_url = mofu_page['url']
            if mofu_url in content:
                log(f"✅ Main Product URL found in content: {mofu_url}")
            else:
                log(f"⚠ Main Product URL NOT found in content. URL: {mofu_url}")
                
            break
        log(f"Waiting... ({i+1}/15)")
    else:
        log("❌ Content generation timed out.")

if __name__ == "__main__":
    test_workflow()
