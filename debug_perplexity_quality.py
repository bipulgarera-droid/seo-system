
import os
import json
import requests

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

def test_perplexity():
    print("🚀 Testing Perplexity Quality for 'SUGAR Tipsy Lips Pinacolada'...")
    
    api_key = os.environ.get('PERPLEXITY_API_KEY')
    if not api_key:
        print("❌ No API Key found")
        return

    # Simulated "Correct" Inputs (what the system SHOULD generate now)
    topic = "Tipsy Lips Moisturizing Balm - 03 Pinacolada | SUGAR Cosmetics"
    location = "India"
    language = "English"
    
    # These would come from the fixed Gemini fallback
    keywords = [
        "sugar tipsy lips pinacolada review",
        "sugar cosmetics lip balm price",
        "best tinted lip balm india",
        "sugar pinacolada lip balm benefits",
        "moisturizing lip balm for dark lips"
    ]
    competitors = [
        "https://in.sugarcosmetics.com/products/tipsy-lips-moisturizing-balm-03-pinacolada",
        "https://www.nykaa.com/sugar-tipsy-lips-moisturizing-balm/p/529792",
        "https://www.amazon.in/SUGAR-Cosmetics-Tipsy-Moisturizing-Balm/dp/B07R9X8X8X"
    ]
    
    keyword_list = ", ".join(keywords)
    competitor_list = ", ".join(competitors)
    
    research_query = f"""
    Research Topic: {topic}
    Top Competitors: {competitor_list}
    Top Keywords: {keyword_list}
    
    Create a detailed Content Research Brief for this topic.
    Analyze the competitors and keywords to find content gaps.
    Focus on User Pain Points, Key Subtopics, and Scientific/Technical details.
    """
    
    print(f"\n--- Sending Query to Perplexity (sonar-pro) ---\n{research_query[:200]}...\n")
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [{
            "role": "user",
            "content": f"""**Role**: You are a Senior Content Strategist.
**CONTEXT**:
- Target Audience Location: {location}
- Target Language: {language}

**LOCALIZATION RULES (CRITICAL)**:
1. **Currency**: You MUST use the local currency for **{location}** (e.g., ₹ INR for India).
2. **Units**: Use the measurement system standard for **{location}**.
3. **Spelling**: Use the correct spelling dialect (e.g., "Colour" for UK/India).

{research_query}"""
        }]
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            data = res.json()
            content = data['choices'][0]['message']['content']
            print("\n✅ Perplexity Response Received:")
            print(content[:1000]) # Print first 1000 chars
            
            if "Strawberry" in content:
                print("\n❌ HALLUCINATION DETECTED: Found 'Strawberry'!")
            else:
                print("\n✅ No 'Strawberry' hallucination found.")
                
            if "₹" in content or "INR" in content:
                print("✅ Currency Localization Verified (₹/INR found)")
            else:
                print("⚠️ Currency Localization Warning (No ₹/INR found)")
                
        else:
            print(f"❌ API Error: {res.status_code} - {res.text}")
            
    except Exception as e:
        print(f"❌ Request Error: {e}")

if __name__ == "__main__":
    test_perplexity()
