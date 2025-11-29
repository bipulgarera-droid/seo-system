import requests
import json
import time

BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

def test_full_localization():
    print("Starting Comprehensive Localization Verification...")
    
    # 1. Fetch Existing Project (Fallback)
    print("\n1. Fetching Existing Project...")
    try:
        res = requests.get(f"{BASE_URL}/api/get-projects", headers=HEADERS)
        if res.status_code == 200:
            projects = res.json().get('projects', [])
            if projects:
                project_id = projects[0]['id']
                print(f"✓ Found existing project: {project_id}")
            else:
                print("✗ No existing projects found.")
                return
        else:
            print(f"✗ Failed to get projects: {res.text}")
            return
    except Exception as e:
        print(f"✗ Error fetching projects: {e}")
        return

    if not project_id: return

    # 2. Add Page (Product)
    print("\n2. Adding Product Page...")
    page_payload = {
        "project_id": project_id,
        "urls": ["https://test-localization-full.com/products/ayurvedic-shampoo"]
    }
    page_id = None
    try:
        res = requests.post(f"{BASE_URL}/api/add-pages", json=page_payload, headers=HEADERS)
        if res.status_code == 200:
            print("✓ Page added successfully")
            # Wait for DB
            time.sleep(2)
            # Fetch pages to get ID
            pages_res = requests.get(f"{BASE_URL}/api/get-pages?project_id={project_id}", headers=HEADERS)
            if pages_res.status_code == 200:
                pages = pages_res.json().get('pages', [])
                if pages:
                    page_id = pages[0]['id']
                    print(f"✓ Found Page ID: {page_id}")
        else:
            print(f"✗ Failed to add page: {res.text}")
            return
    except Exception as e:
        print(f"✗ Error adding page: {e}")
        return

    if not page_id: return

    # 3. Test MoFu Generation (Keyword Research & Topic Gen)
    print("\n3. Testing MoFu Generation...")
    mofu_payload = {
        "page_ids": [page_id],
        "action": "generate_mofu"
    }
    try:
        res = requests.post(f"{BASE_URL}/api/batch-update-pages", json=mofu_payload, headers=HEADERS)
        if res.status_code == 200:
            print("✓ MoFu Generation triggered successfully")
        else:
            print(f"✗ Failed MoFu Generation: {res.text}")
    except Exception as e:
        print(f"✗ Error triggering MoFu: {e}")

    # 4. Test Image Prompt Generation
    print("\n4. Testing Image Prompt Generation...")
    img_payload = {
        "topic": "Benefits of Ayurvedic Shampoo",
        "project_id": project_id
    }
    try:
        res = requests.post(f"{BASE_URL}/api/generate-image-prompt", json=img_payload, headers=HEADERS)
        if res.status_code == 200:
            print(f"✓ Image Prompt Generated: {res.json().get('prompt')[:50]}...")
        else:
            print(f"✗ Failed Image Prompt: {res.text}")
    except Exception as e:
        print(f"✗ Error triggering Image Prompt: {e}")

    print("\n✓ Verification Complete. Check server logs for 'Loc: India' debug prints.")

if __name__ == "__main__":
    test_full_localization()
