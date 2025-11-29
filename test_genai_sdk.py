import os
from google import genai
from google.genai import types

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

def test_new_sdk_grounding():
    print("\n=== TEST: Gemini 2.5 Flash (Grounded) with google-genai SDK ===")
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        tool = types.Tool(google_search=types.GoogleSearch())
        
        print("Sending request...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="What is the current price of Bitcoin in USD right now? Please state the time of your search.",
            config=types.GenerateContentConfig(tools=[tool])
        )
        
        print(f"Response: {response.text}")
        
        # Check for grounding metadata
        # In the new SDK, metadata might be in response.candidates[0].grounding_metadata
        if response.candidates and response.candidates[0].grounding_metadata:
             print("✅ Grounding Metadata Found!")
             print(response.candidates[0].grounding_metadata)
        
        if "Bitcoin" in response.text:
            print("✅ Test Passed")
        else:
            print("⚠️ Test Inconclusive")
            
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_sdk_grounding()
