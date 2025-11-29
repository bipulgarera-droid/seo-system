
import os
import sys
import json
import datetime
from supabase import create_client
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

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def debug_mofu():
    print("🚀 Starting MoFu Debug...")
    
    # 1. Get a Product Page
    print("1. Fetching a Product Page...")
    res = supabase.table('pages').select('*').eq('page_type', 'Product').limit(1).execute()
    if not res.data:
        print("❌ No Product pages found.")
        return
    
    product = res.data[0]
    pid = product['id']
    p_title = product['tech_audit_data'].get('title', 'Unknown Product')
    print(f"   ✓ Found Product: {p_title} ({pid})")
    
    # 2. Fetch Project Settings
    project_res = supabase.table('projects').select('location, language').eq('id', product['project_id']).single().execute()
    project_loc = project_res.data.get('location', 'US') if project_res.data else 'US'
    project_lang = project_res.data.get('language', 'English') if project_res.data else 'English'
    print(f"   ✓ Project Settings: {project_loc} / {project_lang}")

    # 3. Simulate Keyword Fetching (Mocking what happens in index.py)
    print("3. Simulating Keyword Fetching...")
    # We'll just use a dummy list for now to test the GENERATION part
    keyword_list = """
    - best lip balm for dark lips (Vol: 1000, Score: 80)
    - lip balm with spf (Vol: 800, Score: 75)
    - tinted lip balm india (Vol: 600, Score: 70)
    - sugar cosmetics lip balm review (Vol: 400, Score: 60)
    """
    
    # 4. Generate Topics (The Core Logic)
    print("4. Generating Topics with Gemini...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    tool = types.Tool(google_search=types.GoogleSearch())
    
    current_year = datetime.datetime.now().year
    
    topic_prompt = f"""You are an SEO Content Strategist. Generate 6 MoFu (Middle-of-Funnel) article topics based on REAL keyword data.

**Product**: {p_title}
**Target Audience**: {project_loc} ({project_lang})

**VERIFIED HIGH-VOLUME KEYWORDS** (Scored by Opportunity):
{keyword_list}

**YOUR TASK**:
Create 6 MoFu topics. For EACH topic, assign ALL semantically relevant keywords from the list above (could be 3-15 keywords per topic - include as many as naturally fit the angle).

**Requirements**:
1. Each topic must target a primary keyword (highest opportunity score for that angle)
2. Include ALL secondary keywords that semantically match the topic angle
3. Topics should be Middle-of-Funnel (Comparison, Best Of, Guide, vs)

**Topic Types**:
- "Best X for Y in {current_year}" (roundup/comparison)
- "Product vs Competitor" (head-to-head comparison)
- "Top Alternatives to X" (alternative guides)  
- Use cases backed by research

**Output Format** (JSON):
{{
  "topics": [
    {{
      "title": "[Exact title - include year {current_year} if relevant]",
      "slug": "url-friendly-slug",
      "description": "2-sentence description of content angle",
      "keyword_cluster": [
        {{"keyword": "[keyword1]", "volume": 100, "score": 50, "is_primary": true}},
        {{"keyword": "[keyword2]", "volume": 100, "score": 50, "is_primary": false}}
      ],
      "research_notes": "Why this topic (reference SERP competitor or research insight)"
    }}
  ]
}}

CRITICAL: 
1. Use EXACT integers for volume from the provided list. DO NOT write "Estimated".
2. Assign keywords based on semantic relevance. Don't artificially limit - if 12 keywords fit a topic, include all 12.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=topic_prompt,
            config=types.GenerateContentConfig(tools=[tool])
        )
        text = response.text.strip()
        print(f"\n--- Raw Gemini Response ---\n{text[:500]}...\n---------------------------\n")
        
        # Clean JSON
        if text.startswith('```json'): text = text[7:]
        if text.startswith('```'): text = text[3:]
        if text.endswith('```'): text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        topics = data.get('topics', [])
        
        if not topics:
            print("❌ JSON parsed but 'topics' list is empty.")
        else:
            print(f"✅ Successfully generated {len(topics)} topics.")
            print(f"   Sample: {topics[0]['title']}")
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")

if __name__ == "__main__":
    debug_mofu()
