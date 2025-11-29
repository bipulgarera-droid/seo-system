import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('PERPLEXITY_API_KEY')
print(f"API Key found: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("❌ Error: PERPLEXITY_API_KEY not found in environment.")
    exit(1)

url = "https://api.perplexity.ai/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "sonar-pro",
    "messages": [{
        "role": "user",
        "content": "Test query. Reply with 'Pong'."
    }]
}

print("\nSending request to Perplexity...")
try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ Perplexity API is WORKING!")
    else:
        print("\n❌ Perplexity API Failed.")
except Exception as e:
    print(f"\n❌ Request Error: {e}")
