import os
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv()

pplx_key = os.environ.get('PERPLEXITY_API_KEY')

if pplx_key:
    print(f"✓ PERPLEXITY_API_KEY found: {pplx_key[:15]}...{pplx_key[-5:]}")
    
    # Test actual API call
    import requests
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {pplx_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [{
            "role": "user",
            "content": "What is SEO? Give a one sentence answer."
        }],
        "return_citations": True
    }
    
    print("\nTesting Perplexity API...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API WORKS! Response: {data['choices'][0]['message']['content'][:100]}...")
            print(f"Citations: {len(data.get('citations', []))}")
        else:
            print(f"✗ API ERROR: {response.text}")
    except Exception as e:
        print(f"✗ Request failed: {e}")
else:
    print("✗ PERPLEXITY_API_KEY not found in environment")
    print("\nChecking .env file...")
    try:
        with open('.env', 'r') as f:
            content = f.read()
            if 'PERPLEXITY_API_KEY' in content:
                print("✓ Key exists in .env file")
                # Extract the line
                for line in content.split('\n'):
                    if 'PERPLEXITY_API_KEY' in line:
                        print(f"  {line[:50]}...")
            else:
                print("✗ Key NOT in .env file")
    except Exception as e:
        print(f"Could not read .env: {e}")
