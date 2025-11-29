import sys
import os
import json
from dotenv import load_dotenv

# Load env vars
load_dotenv('/Users/bipul/Downloads/seo-saas-brain/.env.local')
load_dotenv('/Users/bipul/Downloads/seo-saas-brain/.env')

# Add api folder to path
sys.path.insert(0, '/Users/bipul/Downloads/seo-saas-brain')
from api.index import perform_gemini_research, research_with_perplexity

print("="*80)
print("🚀 TESTING HYBRID RESEARCH WORKFLOW")
print("="*80)

topic = "best organic face oil for dry skin"
print(f"Topic: {topic}")

# Step 1: Gemini Research (Keywords)
print("\nStep 1: Running Gemini Research (Keywords & Competitors)...")
gemini_result = perform_gemini_research(topic)

if not gemini_result:
    print("❌ Gemini Research Failed!")
    sys.exit(1)

keywords = gemini_result.get('keywords', [])
competitors = gemini_result.get('competitors', [])

print(f"✓ Found {len(competitors)} competitors")
print(f"✓ Found {len(keywords)} keywords")

if len(keywords) < 10:
    print("⚠ Warning: Low keyword count. Check prompt.")
else:
    print("✓ Keyword count looks good.")

print("\nSample Keywords:")
for k in keywords[:5]:
    print(f"  - {k.get('keyword')} ({k.get('intent')})")

# Step 2: Perplexity Research (Brief)
print("\nStep 2: Running Perplexity Research (Brief)...")

keyword_list = ", ".join([k['keyword'] for k in keywords[:15]])
competitor_list = ", ".join([c['url'] for c in competitors])

research_query = f"""
Research Topic: {topic}
Top Competitors: {competitor_list}
Top Keywords: {keyword_list}

Create a detailed Content Research Brief for this topic.
Analyze the competitors and keywords to find content gaps.
Focus on User Pain Points, Key Subtopics, and Scientific/Technical details.
"""

print("Sending query to Perplexity...")
# Uncomment to actually run Perplexity (costs credits)
# perplexity_result = research_with_perplexity(research_query)
# print(f"✓ Perplexity returned {len(perplexity_result.get('research', ''))} chars of research.")

print("\n" + "="*80)
print("🏁 TEST COMPLETE (Perplexity skipped to save credits)")
print("="*80)
