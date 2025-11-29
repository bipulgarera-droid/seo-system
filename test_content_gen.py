import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv('/Users/bipul/Downloads/seo-saas-brain/.env')
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-2.5-pro-preview-03-25')

# Mock Page Data
page_title = "Best Organic Face Oils for Dry Skin (2025 Review)"
funnel_stage = "MoFu"

# Mock Research Data
research_data = {
    "keyword_cluster": [
        {"keyword": "best organic face oil for dry skin", "volume": 1200, "score": 85},
        {"keyword": "natural face oil for dry skin", "volume": 800, "score": 70},
        {"keyword": "face oil for anti aging", "volume": 500, "score": 60}
    ],
    "primary_keyword": "best organic face oil for dry skin",
    "perplexity_research": """
    ## User Pain Points
    - Dry, flaky skin that doesn't respond to lotion.
    - Fear of breakouts from oils (comedogenic concerns).
    - Desire for natural/organic ingredients.
    
    ## Key Subtopics
    - Jojoba vs Argan vs Rosehip oil.
    - How to apply face oil (before or after moisturizer?).
    - Best oils for sensitive skin.
    
    ## Scientific Details
    - Oleic acid is better for dry skin (e.g., Avocado, Olive).
    - Linoleic acid is better for oily skin.
    """,
    "citations": [
        "https://www.healthline.com/health/face-oil-for-dry-skin",
        "https://www.byrdie.com/best-face-oils-for-dry-skin"
    ]
}

internal_links = [
    "- Organic Face Wash Review: https://example.com/face-wash",
    "- Best Moisturizers: https://example.com/moisturizers"
]

links_str = '\n'.join(internal_links)
kw_list = '\n'.join([f"- {kw['keyword']}" for kw in research_data['keyword_cluster']])
citations_str = '\n'.join(research_data['citations'])
perplexity_research = research_data['perplexity_research']

prompt = f"""You are an expert SEO Content Writer following **Google's Complete Search Documentation** (2024/2025):
- Google Search Essentials
- SEO Starter Guide  
- Creating Helpful, Reliable, People-First Content
- E-E-A-T Quality Rater Guidelines

**ARTICLE TYPE**: {funnel_stage} Content
**TOPIC**: {page_title}

**TARGET KEYWORDS** (DataForSEO Validated):
{kw_list}

**VERIFIED RESEARCH** (Perplexity with Citations):
{perplexity_research[:3000]}

**REQUIRED INTERNAL LINKS** (Critical for SEO):
{links_str}

**Sources to Cite**:
{citations_str}

---

**GOOGLE'S MANDATORY REQUIREMENTS** (2024/2025):

**1. E-E-A-T Framework (Quality Rater Guidelines)**:
- **Experience**: Demonstrate first-hand knowledge, testing, or real-world usage
- **Expertise**: Show subject matter authority with detailed, technical insights
- **Authoritativeness**: Cite authoritative sources (use Perplexity citations above)
- **Trustworthiness**: Fact-check all claims, cite sources, admit limitations/uncertainty

**2. Helpful Content Principles (Post-March 2024 Core Update)**:
- Answer search intent DIRECTLY in first paragraph (no fluff intro)
- Provide ORIGINAL insights beyond obvious information
- Include SPECIFIC data/statistics with sources [numbered citations]
- Write for people, not search engines
- Demonstrate expertise through depth and nuance
- Avoid mass-produced, generic content patterns

**3. SEO Starter Guide Essentials**:
- **Title**: Descriptive, unique, includes primary keyword (avoid clickbait)
- **Meta Description**: 150-160 chars, benefit-driven, actionable
- **Headings**: Clear H2/H3 hierarchy matching user questions
- **Internal Linking**: Link to ALL provided internal URLs naturally in content
- **Content Quality**: Substantial, complete, comprehensive (NOT thin or superficial)
- **Mobile-First**: Scannable structure (bullets, short paragraphs)

**4. Featured Snippet Optimization**:
- Provide direct, concise answer in first 2-3 sentences
- Use "Quick Answer" section with 3-5 bullet points
- Structure content to answer "who, what, when, where, why, how"

**5. Structured Data Readiness** (FAQ Schema):
- Include FAQ section with 3-5 common questions
- Format: ### Question / Direct answer (40-50 words)
- Questions should match "People Also Ask" intent

**6. AI Search Optimization** (SearchGPT, Perplexity, Gemini):
   - Clear H2/H3 structure for AI parsing
   - Direct answers to common questions
   - Scannable format (bullet points, tables if relevant)
   - Recent data (2024/2025 stats prioritized)

"""
if any(x in page_title.lower() for x in ['best', 'vs', 'review', 'comparison', 'top']):
    prompt += """
**7. High-Quality Review Standards** (MANDATORY for this topic):
   - Include specific Pros/Cons lists
   - Provide quantitative measurements/metrics where possible
   - Explain *how* things were tested or evaluated
   - Focus on unique features/drawbacks not found in manufacturer specs
"""

prompt += """
---

**INTERNAL LINKING STRATEGY**:

**MANDATORY**: You MUST link to all provided internal links naturally within the content.

**How to Link**:
- MoFu articles: Link to product/pillar pages in context (e.g., "If you're interested in [product name], check out our full review")
- ToFu articles: Link to MoFu articles AND product pages
- Use contextual anchor text (not "click here")
- Link 3-5 times throughout article (intro, middle, conclusion)
- Make links feel natural, not forced

---

**CONTENT STRUCTURE** (Strict Format):

```markdown
**Meta Description**: [150-160 chars, benefit + primary keyword + call-to-action]

# {page_title}

[INTRO: Direct answer to search intent in 2-3 sentences. Include primary keyword. No fluff.]

## Quick Answer
[3-5 bullet points - direct answers for featured snippet targeting]
- [Key point 1]
- [Key point 2]
...

## [H2 matching secondary keyword 1]
[Comprehensive content with Perplexity data. Cite sources [1], [2]. 
**INCLUDE INTERNAL LINK naturally here.**]

### [H3 diving deeper into subtopic]
[Content...]

## [H2 matching secondary keyword 2]
[Content with internal link to another relevant page]

## Frequently Asked Questions

### [Question 1 from keyword research]?
[Direct 40-50 word answer. This becomes FAQ schema.]

### [Question 2]?
[Direct answer...]

### [Question 3]?
[Direct answer...]

## Final Thoughts / Conclusion
[Summary + CTA + internal link to main product/pillar page]

## Sources
1. [Citation 1 with URL]
2. [Citation 2 with URL]
...
```

---

**KEYWORD INTEGRATION**:
- Primary keyword: H1, first paragraph, 2-3 H2/H3 subheadings
- Secondary keywords: H2/H3 topics, naturally throughout
- Semantic variations: Use synonyms and related terms
- Keyword density: 1-2% (natural, not stuffed)

**E-E-A-T SIGNALS** (Critical):
- Every claim cited with [number]
- Phrases: "According to [source], ..." / "Research shows [stat] [1]"
- Admit uncertainty: "While most experts agree... some debate exists about..."
- No absolute statements without sources

**CONTENT QUALITY CHECKLIST** (Google's Self-Assessment):
✓ Original information/analysis (not regurgitated)
✓ Substantial, complete, comprehensive
✓ Insightful beyond the obvious
✓ Worth bookmarking or sharing
✓ Magazine/encyclopedia quality
✓ No spelling/grammar errors
✓ Professional, not sloppy

**WORD COUNT**: 1,800-2,500 words (comprehensive depth)

**OUTPUT**: Full markdown article following structure above. Meta description at top. ALL internal links included.
"""

print("Generating content with Gemini 1.5 Pro...")
response = model.generate_content(prompt)
print("\n" + "="*80)
print(response.text)
print("="*80)
