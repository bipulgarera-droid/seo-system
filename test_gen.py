import requests
import json
import time

API_URL = "http://127.0.0.1:3000/api"
PROJECT_ID = "3eb8f6c4-3200-4402-97f3-9275470701f9" # From previous step

def test_generation():
    print("1. Creating task...")
    res = requests.post(f"{API_URL}/photoshoots", json={
        "project_id": PROJECT_ID,
        "prompt": "A futuristic city with flying cars, cyberpunk style",
        "status": "Pending"
    })
    
    if res.status_code != 200:
        print(f"Failed to create task: {res.text}")
        return
        
    data = res.json()
    if isinstance(data, list):
        task = data[0]
    else:
        task = data.get('photoshoot', data)
        
    task_id = task['id']
    print(f"Task created: {task_id}")
    
    print("2. Triggering generation...")
    start_time = time.time()
    try:
        res = requests.put(f"{API_URL}/photoshoots/{task_id}", json={"action": "run"}, timeout=120)
        print(f"Response status: {res.status_code}")
        print(f"Response text: {res.text}")
        print(f"Time taken: {time.time() - start_time:.2f}s")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_generation()
