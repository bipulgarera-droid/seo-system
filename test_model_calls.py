import google.generativeai as genai
import os
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

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY not found.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

def test_flash_grounding():
    print("\n=== TEST 1: Gemini 2.5 Flash (Grounded) ===")
    try:
        print("Testing Gemini 1.5 Flash 001 (Old Reliable)...")
        tools = [{'google_search': {}}]
        model = genai.GenerativeModel('gemini-1.5-flash-001', tools=tools)
        
        # Ask a question that requires live data
        prompt = "What is the current price of Bitcoin in USD right now? Please state the time of your search."
        print(f"Prompt: {prompt}")
        
        response = model.generate_content(prompt)
        print(f"Response: {response.text}")
        
        if "Bitcoin" in response.text:
            print("✅ 1.5 Flash 001 Grounding Works")
        else:
            print("⚠️ 1.5 Flash 001 Grounding Inconclusive")
            
    except Exception as e:
        print(f"❌ Test Failed: {e}")

def test_pro_stable():
    print("\n=== TEST 2: Gemini 2.5 Pro (Stable) ===")
    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        prompt = "Write a 1-sentence haiku about SEO."
        print(f"Prompt: {prompt}")
        
        response = model.generate_content(prompt)
        print(f"Response: {response.text}")
        
        if response.text:
            print("✅ Pro Stable Test Passed")
        else:
            print("❌ Pro Stable Test Failed (Empty Response)")
            
    except Exception as e:
        print(f"❌ Pro Stable Test Failed: {e}")

if __name__ == "__main__":
    test_flash_grounding()
    test_pro_stable()
