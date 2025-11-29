"""
Test Gemini Keyword Generation
"""
import os
import sys
import json
# Add api directory to path
sys.path.append(os.path.join(os.getcwd(), 'api'))

# Mock env
for env_file in ['.env', '.env.local']:
    env_path = f'/Users/bipul/Downloads/seo-saas-brain/{env_file}'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    val = val.strip('"').strip("'")
                    os.environ[key] = val

from index import perform_gemini_research

topic = "organic face moisturizer"
print(f"Testing Gemini Research for: {topic}")

try:
    result = perform_gemini_research(topic)
    if result:
        keywords = result.get('keywords', [])
        print(f"\n✅ Found {len(keywords)} keywords:")
        for k in keywords[:10]:
            print(f"- {k.get('keyword')} ({k.get('intent')})")
        
        if len(keywords) < 20:
            print("\n⚠ Count is low (< 20). Prompt needs improvement.")
    else:
        print("\n❌ No result returned.")
except Exception as e:
    print(f"\n❌ Error: {e}")
