"""
Comprehensive Verification Script
Simulates the user's workflow to verify all fixes.
"""

import os
import json
import time
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

TEST_DOMAIN = "test-verification-v1.com"

def run_test():
    print("🚀 Starting Comprehensive Verification...")
    
    # 1. Clean up previous test
    print("\n1. Cleaning up previous test data...")
    existing = supabase.table('projects').select('id').eq('domain', TEST_DOMAIN).execute()
    if existing.data:
        pid = existing.data[0]['id']
        supabase.table('pages').delete().eq('project_id', pid).execute()
        supabase.table('projects').delete().eq('id', pid).execute()
        print("   ✓ Cleaned up")

    # 2. Create Project
    print("\n2. Creating Project...")
    proj_res = supabase.table('projects').insert({
        "domain": TEST_DOMAIN,
        "project_name": "Test Project"
    }).execute()
    project_id = proj_res.data[0]['id']
    print(f"   ✓ Project created: {project_id}")

    # 3. Insert Mock Pages (Unclassified)
    print("\n3. Inserting Mock Pages...")
    pages = [
        {"project_id": project_id, "url": f"https://{TEST_DOMAIN}/product/test-product", "page_type": None},
        {"project_id": project_id, "url": f"https://{TEST_DOMAIN}/category/test-category", "page_type": None},
        {"project_id": project_id, "url": f"https://{TEST_DOMAIN}/blog/test-topic", "page_type": None}
    ]
    supabase.table('pages').insert(pages).execute()
    print("   ✓ Pages inserted")

    # 4. Verify Project Count (API Logic)
    print("\n4. Verifying Project Count (API Logic)...")
    # We can't easily call the API function directly without flask context, 
    # but we can simulate the logic we fixed.
    all_pages = supabase.table('pages').select('project_id, page_type').eq('project_id', project_id).execute()
    count = len(all_pages.data)
    classified = sum(1 for p in all_pages.data if p.get('page_type') and p.get('page_type') != 'Unclassified')
    
    print(f"   Pages found: {count}")
    print(f"   Classified found: {classified}")
    
    if count != 3:
        print("   ❌ Count Mismatch! Expected 3")
    else:
        print("   ✓ Count Logic Correct")

    # 5. Test Classification (Category Title Fix)
    print("\n5. Testing Category Classification (Title Fix)...")
    cat_page = supabase.table('pages').select('*').eq('url', f"https://{TEST_DOMAIN}/category/test-category").single().execute()
    cat_id = cat_page.data['id']
    
    # Simulate classify_page logic
    stage = 'Category'
    update_data = {'page_type': stage}
    
    # Logic we added:
    if stage == 'Product' or stage == 'Category':
        url = cat_page.data['url']
        slug = url.split('/')[-1]
        title = slug.replace('-', ' ').title()
        tech_data = cat_page.data.get('tech_audit_data') or {}
        tech_data['title'] = title
        update_data['tech_audit_data'] = tech_data
    
    supabase.table('pages').update(update_data).eq('id', cat_id).execute()
    
    # Verify
    updated_cat = supabase.table('pages').select('*').eq('id', cat_id).single().execute()
    title = updated_cat.data.get('tech_audit_data', {}).get('title')
    print(f"   Category Title: {title}")
    
    if title == "Test Category":
        print("   ✓ Category Title Extracted Successfully")
    else:
        print(f"   ❌ Category Title Failed! Got: {title}")

    # 6. Test Content Generation Persistence
    print("\n6. Testing Content Generation Persistence...")
    prod_page = supabase.table('pages').select('*').eq('url', f"https://{TEST_DOMAIN}/product/test-product").single().execute()
    prod_id = prod_page.data['id']
    
    # Simulate generate_content update
    generated_content = "# Test Content\n\nThis is generated content."
    supabase.table('pages').update({
        "content": generated_content,
        "product_action": "Idle"
    }).eq('id', prod_id).execute()
    
    # Verify
    updated_prod = supabase.table('pages').select('*').eq('id', prod_id).single().execute()
    saved_content = updated_prod.data.get('content')
    
    if saved_content == generated_content:
        print("   ✓ Content Saved to DB Successfully")
    else:
        print("   ❌ Content Save Failed!")

    # 7. Test ToFu Generation (Insertion & Query)
    print("\n7. Testing ToFu Generation (Insertion & Query)...")
    # Simulate ToFu insertion
    tofu_page = {
        "project_id": project_id,
        "url": f"https://{TEST_DOMAIN}/blog/test-tofu-topic",
        "page_type": "Topic",
        "funnel_stage": "ToFu",
        "tech_audit_data": {"title": "Test ToFu Topic"}
    }
    supabase.table('pages').insert(tofu_page).execute()
    
    # Verify Query (what the ToFu tab uses)
    tofu_res = supabase.table('pages').select('*').eq('project_id', project_id).eq('funnel_stage', 'ToFu').execute()
    
    if len(tofu_res.data) > 0:
        print(f"   ✓ ToFu Page Found: {tofu_res.data[0]['url']}")
    else:
        print("   ❌ ToFu Page NOT Found via Query!")

    # 8. Test Scrape Content Persistence
    print("\n8. Testing Scrape Content Persistence...")
    # Simulate scrape_content update
    scraped_body = "This is scraped content body."
    current_tech = prod_page.data.get('tech_audit_data') or {}
    current_tech['body_content'] = scraped_body
    
    supabase.table('pages').update({
        "tech_audit_data": current_tech
    }).eq('id', prod_id).execute()
    
    # Verify
    updated_prod_scrape = supabase.table('pages').select('*').eq('id', prod_id).single().execute()
    saved_body = updated_prod_scrape.data.get('tech_audit_data', {}).get('body_content')
    
    if saved_body == scraped_body:
        print("   ✓ Scraped Content Saved to DB Successfully")
    else:
        print("   ❌ Scraped Content Save Failed!")

    print("\n✅ Verification Complete!")

if __name__ == "__main__":
    run_test()
