"""
Test script to verify Scrape Content and Generate MoFu functionality.
"""

import os
import requests
import json

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

API_BASE = "http://localhost:3000"
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("TESTING SCRAPE CONTENT AND GENERATE MOFU FUNCTIONALITY")
print("=" * 80)

# Test 1: Find a Product page to test with
print("\n[TEST 1] Finding a Product page...")
try:
    result = supabase.table('pages').select('*').eq('page_type', 'Product').limit(1).execute()
    
    if result.data and len(result.data) > 0:
        product_page = result.data[0]
        print(f"✅ Found Product page: {product_page['url']}")
        print(f"   Page ID: {product_page['id']}")
        product_id = product_page['id']
    else:
        print("❌ No Product pages found in database!")
        print("   Please add a Product page first in the URL Classification tab.")
        exit(1)
        
except Exception as e:
    print(f"❌ Error querying database: {e}")
    exit(1)

# Test 2: Test Scrape Content
print("\n[TEST 2] Testing Scrape Content...")
try:
    response = requests.post(
        f"{API_BASE}/api/batch-update-pages",
        json={
            "page_ids": [product_id],
            "action": "scrape_content"
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Scrape Content SUCCESS")
        print(f"   Response: {data}")
        
        # Verify the content was scraped
        updated = supabase.table('pages').select('tech_audit_data').eq('id', product_id).single().execute()
        if updated.data and updated.data.get('tech_audit_data', {}).get('body_content'):
            print(f"✅ Content verified in database")
            print(f"   Content length: {len(updated.data['tech_audit_data']['body_content'])} chars")
        else:
            print(f"⚠️  Content not found in database after scrape")
    else:
        print(f"❌ Scrape Content FAILED")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error testing scrape_content: {e}")

# Test 3: Test Generate MoFu
print("\n[TEST 3] Testing Generate MoFu...")
try:
    response = requests.post(
        f"{API_BASE}/api/batch-update-pages",  # Fixed: added /api/ prefix
        json={
            "page_ids": [product_id],
            "action": "generate_mofu"
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Generate MoFu SUCCESS")
        print(f"   Response: {data}")
        
        # Check if MoFu topics were created
        mofu_topics = supabase.table('pages').select('*').eq('source_page_id', product_id).eq('funnel_stage', 'MoFu').execute()
        if mofu_topics.data:
            print(f"✅ MoFu topics created: {len(mofu_topics.data)} topics")
            for topic in mofu_topics.data[:3]:  # Show first 3
                tech_data = topic.get('tech_audit_data', {})
                title = tech_data.get('title', 'No title') if isinstance(tech_data, dict) else 'No title'
                print(f"   - {title}")
        else:
            print(f"⚠️  No MoFu topics found (might be processing)")
    else:
        print(f"❌ Generate MoFu FAILED")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error testing generate_mofu: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
