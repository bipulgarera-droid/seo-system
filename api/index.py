import os
import time
import traceback
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import re
from supabase import create_client, Client
from dotenv import load_dotenv
import io
import mimetypes

load_dotenv('.env.local')
load_dotenv()

app = Flask(__name__, static_folder='../public', static_url_path='')
CORS(app)

import logging
logging.basicConfig(filename='backend.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger()

# Redirect print to logger
def print(*args, **kwargs):
    logger.info(" ".join(map(str, args)))

# Configure Gemini
# Configure Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # In production, this should ideally log an error or fail gracefully if the key is critical
    pass 
genai.configure(api_key=GEMINI_API_KEY)

# Configure Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

@app.route('/')
def home():
    return app.send_static_file('agency.html')

@app.route('/api/test-ai', methods=['POST'])
def test_ai():
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY not found"}), 500

    try:
        data = request.get_json()
        topic = data.get('topic', 'SaaS Marketing') if data else 'SaaS Marketing'

        # Using the requested model which is confirmed to be available for this key
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(f"Write a short 1-sentence SEO strategy for '{topic}'.")
        return jsonify({"strategy": response.text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/start-audit', methods=['POST'])
def start_audit():
    print("DEBUG: AUDIT FIX APPLIED - STARTING REQUEST")
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500

    try:
        data = request.get_json()
        page_id = data.get('page_id')
        
        if not page_id:
            return jsonify({"error": "page_id is required"}), 400
        
        # 1. Get the page
        page_res = supabase.table('pages').select('*').eq('id', page_id).execute()
        if not page_res.data:
            return jsonify({"error": "Page not found"}), 404
        
        page = page_res.data[0]
        target_url = page['url']
        
        print(f"DEBUG: Starting Tech Audit for {target_url}")
        
        # 2. Update status to PROCESSING
        supabase.table('pages').update({"audit_status": "Processing"}).eq('id', page_id).execute()
        
        # 3. Perform Tech Audit
        audit_data = {
            "status_code": None,
            "load_time_ms": 0,
            "title": None,
            "meta_description": None,
            "h1": None,
            "word_count": 0,
            "internal_links_count": 0,
            "broken_links": []
        }
        
        try:
            start_time = time.time()
            # Use a real browser User-Agent to avoid 403 Forbidden on sites like Apple
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(target_url, headers=headers, timeout=15)
            audit_data["load_time_ms"] = int((time.time() - start_time) * 1000)
            audit_data["status_code"] = response.status_code
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Title
                audit_data["title"] = soup.title.string.strip() if soup.title else None
                
                # Meta Description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    audit_data["meta_description"] = meta_desc.get('content', '').strip()
                
                # H1
                h1 = soup.find('h1')
                audit_data["h1"] = h1.get_text().strip() if h1 else None

                # Open Graph Tags
                og_title = soup.find('meta', attrs={'property': 'og:title'})
                audit_data["og_title"] = og_title.get('content', '').strip() if og_title else None
                
                og_desc = soup.find('meta', attrs={'property': 'og:description'})
                audit_data["og_description"] = og_desc.get('content', '').strip() if og_desc else None
                
                # Word Count (rough estimate)
                text = soup.get_text(separator=' ')
                words = [w for w in text.split() if len(w) > 2]
                audit_data["word_count"] = len(words)
                
                # Internal Links
                links = soup.find_all('a', href=True)
                audit_data["internal_links_count"] = len(links)

                # Canonical
                canonical = soup.find('link', attrs={'rel': 'canonical'})
                if canonical:
                    audit_data["canonical"] = canonical.get('href', '').strip()
                
                # Click Depth (Estimated based on URL path segments)
                import urllib.parse
                path = urllib.parse.urlparse(target_url).path
                # Root / is depth 0 or 1. Let's say root is 0.
                segments = [x for x in path.split('/') if x]
                audit_data["click_depth"] = len(segments)

                # --- On-Page Analysis ---
                score = 100
                checks = []
                
                # Title Analysis
                title = audit_data.get("title")
                if not title:
                    score -= 20
                    checks.append("Missing Title")
                    audit_data["title_length"] = 0
                else:
                    t_len = len(title)
                    audit_data["title_length"] = t_len
                    if t_len < 10: 
                        score -= 10
                        checks.append("Title too short")
                    elif t_len > 60:
                        score -= 10
                        checks.append("Title too long")

                # Meta Description Analysis
                desc = audit_data.get("meta_description")
                if not desc:
                    score -= 20
                    checks.append("Missing Meta Desc")
                    audit_data["description_length"] = 0
                else:
                    d_len = len(desc)
                    audit_data["description_length"] = d_len
                    if d_len < 50:
                        score -= 5
                        checks.append("Desc too short")
                    elif d_len > 160:
                        score -= 5
                        checks.append("Desc too long")

                # H1 Analysis
                h1 = audit_data.get("h1")
                if not h1:
                    score -= 20
                    checks.append("Missing H1")
                    audit_data["missing_h1"] = True
                else:
                    audit_data["missing_h1"] = False

                # OG Checks
                if not audit_data.get("og_title"):
                    checks.append("Missing OG Title")
                if not audit_data.get("og_description"):
                    checks.append("Missing OG Desc")
                
                # Image Alt Analysis
                images = soup.find_all('img')
                missing_alt = [img for img in images if not img.get('alt')]
                audit_data["missing_alt_count"] = len(missing_alt)
                
                if missing_alt:
                    score -= 10
                    checks.append(f"{len(missing_alt)} Images missing Alt")
                
                # --- Technical Issues Checks ---
                # Check for redirects using history
                if response.history:
                    audit_data["is_redirect"] = True
                    # You might want to store the initial status, but for now let's keep the final status for on-page checks
                    # or maybe store initial_status separately if needed.
                    # audit_data["status_code"] = response.history[0].status_code # Optional: if you want the 301
                else:
                    audit_data["is_redirect"] = 300 <= response.status_code < 400

                status = audit_data["status_code"]
                audit_data["is_4xx_code"] = 400 <= status < 500
                audit_data["is_5xx_code"] = 500 <= status < 600
                audit_data["high_loading_time"] = audit_data["load_time_ms"] > 2000
                
                # Advanced Checks
                audit_data["redirect_chain"] = len(response.history) > 1
                
                canonical = audit_data.get("canonical")
                if canonical and canonical != target_url:
                    audit_data["canonical_mismatch"] = True
                else:
                    audit_data["canonical_mismatch"] = False
                    
                audit_data["is_orphan_page"] = False # Placeholder: Requires full link graph
                
                # Final Checks
                audit_data["is_broken"] = status >= 400 or status == 0
                
                # Schema / Microdata Check
                has_json_ld = soup.find('script', type='application/ld+json') is not None
                has_microdata = soup.find(attrs={'itemscope': True}) is not None
                audit_data["has_schema"] = has_json_ld or has_microdata
                
                # Duplicate Checks (Query DB)
                try:
                    if title:
                        dup_title = supabase.table('pages').select('id', count='exact').eq('title', title).neq('id', page_id).execute()
                        audit_data["duplicate_title"] = dup_title.count > 0
                    else:
                        audit_data["duplicate_title"] = False
                        
                    if desc:
                        dup_desc = supabase.table('pages').select('id', count='exact').eq('meta_description', desc).neq('id', page_id).execute()
                        audit_data["duplicate_desc"] = dup_desc.count > 0
                    else:
                        audit_data["duplicate_desc"] = False
                except Exception as e:
                    print(f"Duplicate Check Error: {e}")
                    audit_data["duplicate_title"] = False
                    audit_data["duplicate_desc"] = False

                audit_data["onpage_score"] = max(0, score)
                audit_data["checks"] = checks

            else:
                print(f"Audit Failed: Status {response.status_code}")
                audit_data["error"] = f"HTTP {response.status_code}"
                audit_data["onpage_score"] = 0
                
        except Exception as e:
            print(f"Audit Error: {e}")
            audit_data["error"] = str(e)
            audit_data["status_code"] = 0 # Indicate failure
    
    # 4. Save Results (Merge with existing)
        current_tech_data = page.get('tech_audit_data') or {}
        current_tech_data.update(audit_data)
        
        update_payload = {
            "audit_status": "Analyzed",
            "tech_audit_data": current_tech_data,
            # Also update core fields if found
            "title": audit_data.get("title") or page.get("title"),
            "meta_description": audit_data.get("meta_description") or page.get("meta_description"),
            "h1": audit_data.get("h1") or page.get("h1")
        }
        
        print(f"DEBUG: Updating DB for page {page_id}")
        print(f"DEBUG: Payload: {json.dumps(update_payload, default=str)[:500]}...") # Print first 500 chars
        
        res = supabase.table('pages').update(update_payload).eq('id', page_id).execute()
        print(f"DEBUG: DB Update Result: {res}")
        
        return jsonify({
            "message": "Tech audit completed",
            "data": audit_data
        })

    except Exception as e:
        print(f"ERROR in start_audit: {str(e)}")
        import traceback
        traceback.print_exc()
        supabase.table('pages').update({"audit_status": "Failed"}).eq('id', page_id).execute()
        return jsonify({"error": str(e)}), 500

        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-speed', methods=['POST'])
def analyze_speed():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        strategy = data.get('strategy', 'mobile') # mobile or desktop
        
        if not page_id: return jsonify({"error": "page_id required"}), 400
        
        # Fetch Page
        page_res = supabase.table('pages').select('url, tech_audit_data').eq('id', page_id).single().execute()
        if not page_res.data: return jsonify({"error": "Page not found"}), 404
        page = page_res.data
        url = page['url']
        
        print(f"Running PageSpeed ({strategy}) for {url}...")
        
        # Call Google PageSpeed Insights API
        psi_key = os.environ.get("PAGESPEED_API_KEY")
        psi_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy={strategy}"
        if psi_key:
            psi_url += f"&key={psi_key}"
            
        psi_res = requests.get(psi_url, timeout=60)
        
        if psi_res.status_code != 200:
            return jsonify({"error": f"PSI API Failed: {psi_res.text}"}), 400
            
        psi_data = psi_res.json()
        
        # Extract Metrics
        lighthouse = psi_data.get('lighthouseResult', {})
        audits = lighthouse.get('audits', {})
        categories = lighthouse.get('categories', {})
        
        score = categories.get('performance', {}).get('score', 0) * 100
        fcp = audits.get('first-contentful-paint', {}).get('displayValue')
        lcp = audits.get('largest-contentful-paint', {}).get('displayValue')
        cls = audits.get('cumulative-layout-shift', {}).get('displayValue')
        tti = audits.get('interactive', {}).get('displayValue')
        
        # Update DB
        current_data = page.get('tech_audit_data') or {}
        speed_data = current_data.get('speed', {})
        speed_data[strategy] = {
            "score": score,
            "fcp": fcp,
            "lcp": lcp,
            "cls": cls,
            "tti": tti,
            "last_run": int(time.time())
        }
        current_data['speed'] = speed_data
        
        supabase.table('pages').update({"tech_audit_data": current_data}).eq('id', page_id).execute()
        
        return jsonify({
            "message": "Speed analysis complete",
            "data": speed_data[strategy]
        })
        
    except Exception as e:
        print(f"Speed Audit Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-page-status', methods=['POST'])
def update_page_status():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        updates = {}
        
        if 'funnel_stage' in data:
            updates['funnel_stage'] = data['funnel_stage']
            
        if 'page_type' in data:
            updates['page_type'] = data['page_type']
            
            # Auto-fetch title if classifying as Product and title is missing
            if data['page_type'] == 'Product':
                try:
                    # Get current page data
                    page_res = supabase.table('pages').select('url, tech_audit_data').eq('id', page_id).execute()
                    if page_res.data:
                        page = page_res.data[0]
                        tech_data = page.get('tech_audit_data') or {}
                        
                        if not tech_data.get('title') or tech_data.get('title') == 'Untitled Product':
                            print(f"Auto-fetching title for {page['url']}...")
                            try:
                                resp = requests.get(page['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                                if resp.status_code == 200:
                                    soup = BeautifulSoup(resp.content, 'html.parser')
                                    if soup.title and soup.title.string:
                                        raw_title = soup.title.string.strip()
                                        new_title = clean_title(raw_title)
                                        tech_data['title'] = new_title
                                        updates['tech_audit_data'] = tech_data
                                        print(f"Fetched title: {new_title}")
                            except Exception as scrape_err:
                                print(f"Scrape failed: {scrape_err}")
                except Exception as e:
                    print(f"Auto-fetch error: {e}")

        if 'approval_status' in data:
            updates['approval_status'] = data['approval_status']
            
        if not updates:
            return jsonify({"error": "No updates provided"}), 400
            
        supabase.table('pages').update(updates).eq('id', page_id).execute()
        return jsonify({"message": "Page updated successfully", "updates": updates})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import requests
from urllib.parse import urlparse

# ... (existing imports)

# Configure DataForSEO
DATAFORSEO_LOGIN = os.environ.get("DATAFORSEO_LOGIN")
DATAFORSEO_PASSWORD = os.environ.get("DATAFORSEO_PASSWORD")

def get_ranking_keywords(target_url):
    if not DATAFORSEO_LOGIN or not DATAFORSEO_PASSWORD:
        print("DataForSEO credentials missing.")
        return []

    try:
        # Clean URL to get domain (DataForSEO prefers domain without protocol)
        parsed = urlparse(target_url)
        domain = parsed.netloc if parsed.netloc else parsed.path
        if domain.startswith("www."):
            domain = domain[4:]
        
        # Normalize the target URL for comparison (remove protocol, www, trailing slash)
        normalized_target = target_url.lower().replace('https://', '').replace('http://', '').replace('www.', '').rstrip('/')
        
        print(f"DEBUG: Looking for keywords for normalized URL: {normalized_target}")

        url = "https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live"
        payload = [
            {
                "target": domain,
                "location_code": 2840, # US
                "language_code": "en",
                "filters": [
                    ["ranked_serp_element.serp_item.rank_absolute", ">=", 1],
                    "and",
                    ["ranked_serp_element.serp_item.rank_absolute", "<=", 10]
                ],
                "order_by": ["keyword_data.keyword_info.search_volume,desc"],
                "limit": 100  # Get more results to filter
            }
        ]
        headers = {
            'content-type': 'application/json'
        }

        response = requests.post(url, json=payload, auth=(DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD), headers=headers)
        response.raise_for_status()
        data = response.json()

        page_keywords = []
        domain_keywords = []
        
        if data['tasks'] and data['tasks'][0]['result'] and data['tasks'][0]['result'][0]['items']:
            for item in data['tasks'][0]['result'][0]['items']:
                keyword = item['keyword_data']['keyword']
                volume = item['keyword_data']['keyword_info']['search_volume']
                
                # Get the ranking URL for this keyword
                ranking_url = item.get('ranked_serp_element', {}).get('serp_item', {}).get('url', '')
                # Normalize ranking URL the same way
                normalized_ranking = ranking_url.lower().replace('https://', '').replace('http://', '').replace('www.', '').rstrip('/')
                
                # Check if this keyword ranks for the specific page
                if normalized_ranking == normalized_target:
                    page_keywords.append(f"{keyword} (Vol: {volume})")
                    print(f"DEBUG: ✓ Page match: {keyword} ranks for {normalized_ranking}")
                elif normalized_ranking.startswith(domain):
                    domain_keywords.append(f"{keyword} (Vol: {volume})")
        
        # If we found page-specific keywords, return those (up to 5)
        if page_keywords:
            print(f"DEBUG: ✓ Found {len(page_keywords)} page-specific keywords for {target_url}")
            return page_keywords[:5]
        
        # Otherwise, return only 3 domain keywords as fallback
        if domain_keywords:
            print(f"DEBUG: ⚠ No page-specific keywords found. Using 3 domain-level keywords as fallback")
            return domain_keywords[:3]
        
        print(f"DEBUG: ✗ No keywords found at all for {target_url}")
        return []

    except Exception as e:
        print(f"DataForSEO Error: {e}")
        import traceback
        traceback.print_exc()
        return []

@app.route('/api/process-job', methods=['POST'])
def process_job():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500

    try:
        # Step A: Fetch one pending job
        response = supabase.table('audit_results').select("*").eq('status', 'PENDING').limit(1).execute()
        
        if not response.data:
            return jsonify({"message": "No pending jobs"})
        
        job = response.data[0]
        job_id = job['id']
        target_url = job.get('url')
        if not target_url:
            target_url = 'example.com'
        
        # Step B: Lock (Update status to PROCESSING)
        supabase.table('audit_results').update({"status": "PROCESSING"}).eq('id', job_id).execute()
        
        # Step C: Work (Generate SEO audit)
        
        # 1. Get Keywords (Graceful degradation)
        keywords = get_ranking_keywords(target_url)
        keywords_str = ", ".join(keywords) if keywords else "No specific ranking keywords found."

        # 2. Generate Audit with Gemini
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"Analyze SEO for {target_url}. It currently ranks for these top keywords: {keywords_str}. Based on this, suggest 3 new content topics."
        
        ai_response = model.generate_content(prompt)
        audit_result = ai_response.text.strip()
        
        # Step D: Save (Update result and status to COMPLETED)
        supabase.table('audit_results').update({
            "status": "COMPLETED",
            "result": audit_result
        }).eq('id', job_id).execute()
        
        return jsonify({
            "id": job_id,
            "status": "COMPLETED",
            "result": audit_result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/write-article', methods=['POST'])
def write_article():
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY not found"}), 500

    try:
        data = request.get_json()
        topic = data.get('topic')
        keywords = data.get('keywords', [])

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_instruction = "You are an expert SEO content writer. Write a comprehensive, engaging 1,500-word blog post about the given topic. Use H2 and H3 headers. Format in Markdown. Include a catchy title."
        
        keywords_str = ', '.join(keywords) if keywords else 'relevant SEO keywords'
        full_prompt = f"{system_instruction}\n\nTopic: {topic}\nTarget Keywords: {keywords_str}"
        
        response = model.generate_content(full_prompt)
        return jsonify({"content": response.text.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

from bs4 import BeautifulSoup

# ... (existing imports)



def crawl_sitemap(domain, project_id, max_pages=200):
    """Recursively crawl sitemaps with anti-bot headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    base_domain = domain if domain.startswith('http') else f"https://{domain}"
    sitemap_urls = []
    
    # 1. Try robots.txt first
    robots_url = f"{base_domain}/robots.txt"
    print(f"DEBUG: Fetching robots.txt: {robots_url}")
    try:
        robots_res = requests.get(robots_url, headers=headers, timeout=10)
        if robots_res.status_code == 200:
            for line in robots_res.text.splitlines():
                if line.lower().startswith('sitemap:'):
                    sitemap_url = line.split(':', 1)[1].strip()
                    sitemap_urls.append(sitemap_url)
            print(f"DEBUG: Found {len(sitemap_urls)} sitemaps in robots.txt")
    except Exception as e:
        print(f"DEBUG: Failed to fetch robots.txt: {e}")

    # 2. Fallback to common paths
    if not sitemap_urls:
        sitemap_urls = [
            f"{base_domain}/sitemap.xml",
            f"{base_domain}/sitemap_index.xml",
            f"{base_domain}/sitemap.php"
        ]

    pages = []
    
    # 3. Process each sitemap
    for sitemap_url in sitemap_urls:
        if len(pages) >= max_pages:
            break
        pages.extend(fetch_sitemap_urls(sitemap_url, project_id, headers, max_pages - len(pages)))
    
    return pages

def clean_title(title):
    """Clean up product titles by removing common e-commerce patterns."""
    if not title: return "Untitled Product"
    
    # Remove "Buy " from start (case insensitive)
    import re
    title = re.sub(r'^buy\s+', '', title, flags=re.IGNORECASE)
    
    # Remove " Online" from end (case insensitive)
    title = re.sub(r'\s+online$', '', title, flags=re.IGNORECASE)
    
    # Remove " - [Brand]" or " | [Brand]" suffix
    # Heuristic: split by " - " or " | " and take the first part if it's long enough
    separators = [" - ", " | ", " – "]
    for sep in separators:
        if sep in title:
            parts = title.split(sep)
            if len(parts[0]) > 3: # Avoid cutting too much if title is short
                title = parts[0]
                break
                
    return title.strip()

def fetch_sitemap_urls(sitemap_url, project_id, headers, max_urls):
    """Fetch URLs from a sitemap, recursively handling sitemap indexes"""
    print(f"DEBUG: Fetching sitemap: {sitemap_url}")
    pages = []
    
    try:
        response = requests.get(sitemap_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"DEBUG: Failed to fetch {sitemap_url} (Status {response.status_code})")
            return pages

        # Try parsing with XML, fallback to HTML parser if needed
        try:
            soup = BeautifulSoup(response.content, 'xml')
        except:
            soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check if this is a sitemap index (contains <sitemap> tags)
        sitemap_tags = soup.find_all('sitemap')
        
        if sitemap_tags:
            print(f"DEBUG: Found sitemap index with {len(sitemap_tags)} child sitemaps")
            # Recursively fetch first 5 child sitemaps (increased from 2)
            for i, sitemap_tag in enumerate(sitemap_tags[:5]):
                if len(pages) >= max_urls:
                    break
                    
                loc = sitemap_tag.find('loc')
                if loc:
                    child_url = loc.text.strip()
                    print(f"DEBUG: Recursively fetching child sitemap {i+1}: {child_url}")
                    child_pages = fetch_sitemap_urls(child_url, project_id, headers, max_urls - len(pages))
                    pages.extend(child_pages)
        else:
            # Regular sitemap with <url> tags
            url_tags = soup.find_all('url')
            print(f"DEBUG: Found {len(url_tags)} URLs in sitemap")
            
            for tag in url_tags:
                if len(pages) >= max_urls:
                    break
                    
                loc = tag.find('loc')
                if loc and loc.text.strip():
                    url = loc.text.strip()
                    
                    # Basic scraping to get title
                    title = "Untitled Product"
                    try:
                        page_res = requests.get(url, headers=headers, timeout=10)
                        if page_res.status_code == 200:
                            page_soup = BeautifulSoup(page_res.content, 'html.parser')
                            if page_soup.title and page_soup.title.string:
                                raw_title = page_soup.title.string.strip()
                                title = clean_title(raw_title)
                    except Exception as e:
                        print(f"Failed to scrape title for {url}: {e}")

                    pages.append({
                        'project_id': project_id,
                        'url': url,
                        'status': 'DISCOVERED',
                        'tech_audit_data': {'title': title} # Save title here
                    })
    
    except Exception as e:
        print(f"DEBUG: Error fetching sitemap {sitemap_url}: {e}")
    
    return pages


# Helper function to upload to Supabase Storage
def upload_to_supabase(file_data, filename, bucket_name='photoshoots'):
    """
    Uploads file data (bytes) to Supabase Storage and returns the public URL.
    """
    import mimetypes
    try:
        # Guess mime type
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = 'application/octet-stream'
            
        # Upload
        res = supabase.storage.from_(bucket_name).upload(
            path=filename,
            file=file_data,
            file_options={"content-type": mime_type, "upsert": "true"}
        )
        
        # Get Public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
        return public_url
    except Exception as e:
        print(f"Supabase Upload Error: {e}")
        raise e

# Helper to load image from URL or Path
def load_image_data(source):
    """
    Loads image data from a URL (starts with http) or local path.
    Returns PIL Image object.
    """
    import PIL.Image
    import io
    import os
    if source.startswith('http'):
        print(f"Downloading image from URL: {source}")
        resp = requests.get(source)
        resp.raise_for_status()
        return PIL.Image.open(io.BytesIO(resp.content))
    else:
        # Assume local path relative to public
        # Handle cases where source might be just filename or /uploads/filename
        clean_path = source.lstrip('/')
        local_path = os.path.join(os.getcwd(), 'public', clean_path)
        print(f"Loading image from local path: {local_path}")
        if os.path.exists(local_path):
            return PIL.Image.open(local_path)
        else:
            # Try absolute path just in case
            if os.path.exists(source):
                return PIL.Image.open(source)
            raise Exception(f"Image not found at {source} or {local_path}")

@app.route('/api/health', methods=['GET'])
def health_check():
    print("Health check received")
    db_status = "unknown"
    try:
        # Try a simple query
        if supabase:
            res = supabase.table('projects').select('id').limit(1).execute()
            db_status = "connected"
        else:
            db_status = "not_configured"
    except Exception as e:
        print(f"DB Check failed: {e}")
        db_status = f"error: {str(e)}"
        
    return jsonify({"status": "ok", "message": "Backend is running", "database": db_status})

@app.route('/api/get-projects', methods=['GET'])
def get_projects():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        # Fetch projects
        projects_res = supabase.table('projects').select('*').order('created_at', desc=True).execute()
        projects = projects_res.data if projects_res.data else []
        
        if not projects:
            return jsonify({"projects": []})
        
        # Fetch profiles for these projects
        try:
            profiles_res = supabase.table('business_profiles').select('*').execute()
            profiles_data = profiles_res.data if profiles_res.data else []
            profiles_map = {p['project_id']: p for p in profiles_data}
        except Exception as e:
            print(f"Error fetching profiles: {e}")
            profiles_map = {}
        
        # Fetch all pages for counts (optimization)
        try:
            all_pages_res = supabase.table('pages').select('project_id, page_type').execute()
            all_pages = all_pages_res.data if all_pages_res.data else []
        except Exception as e:
            print(f"Error fetching pages for counts: {e}")
            all_pages = []
        
        from collections import defaultdict
        counts = defaultdict(int)
        classified_counts = defaultdict(int)
        
        for page in all_pages:
            pid = page.get('project_id')
            if pid:
                counts[pid] += 1
                if page.get('page_type') != 'Unclassified':
                    classified_counts[pid] += 1

        # Merge and parse strategy plan
        final_projects = []
        for p in projects:
            try:
                profile = profiles_map.get(p['id'], {})
                
                # Parse Strategy Plan from Business Summary if present (WORKAROUND)
                summary = profile.get('business_summary') or ''
                strategy_plan = ''
                if '===STRATEGY_PLAN===' in summary:
                    try:
                        parts = summary.split('===STRATEGY_PLAN===')
                        summary = parts[0].strip()
                        if len(parts) > 1:
                            strategy_plan = parts[1].strip()
                    except:
                        pass
                
                # Construct the project object to return
                project_obj = {
                    "id": p['id'],
                    "project_name": p['project_name'],
                    "domain": p['domain'],
                    "language": p['language'],
                    "location": p['location'],
                    "focus": p['focus'],
                    "created_at": p['created_at'],
                    "business_summary": summary, # Cleaned summary
                    "strategy_plan": strategy_plan, # Extracted strategy
                    "ideal_customer_profile": profile.get('ideal_customer_profile'),
                    "brand_voice": profile.get('brand_voice'),
                    "primary_products": profile.get('primary_products'),
                    "competitors": profile.get('competitors'),
                    "unique_selling_points": profile.get('unique_selling_points'),
                    "page_count": counts.get(p['id'], 0),
                    "classified_count": classified_counts.get(p['id'], 0)
                }
                final_projects.append(project_obj)
            except Exception as e:
                print(f"Error processing project {p.get('id')}: {e}")
                continue
            
        return jsonify({"projects": final_projects})
    except Exception as e:
        print(f"Critical error in get_projects: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-pages', methods=['GET'])
def get_pages():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        project_id = request.args.get('project_id')
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        response = supabase.table('pages').select('*').eq('project_id', project_id).execute()
        return jsonify({"pages": response.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create-project', methods=['POST'])
def create_project():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    
    data = request.get_json()
    domain = data.get('domain')
    project_name = data.get('project_name', domain)
    language = data.get('language', 'English')
    location = data.get('location', 'US')
    focus = data.get('focus', 'Product')
    
    if not domain:
        return jsonify({"error": "Domain is required"}), 400
        
    try:
        # 1. Create Project
        print(f"Creating project for {domain}...")
        project_res = supabase.table('projects').insert({
            "domain": domain,
            "project_name": project_name,
            "language": language,
            "location": location,
            "focus": focus
        }).execute()
        
        if not project_res.data:
            raise Exception("Failed to create project")
            
        project_id = project_res.data[0]['id']
        print(f"Project created: {project_id}")
        
        return jsonify({
            "message": "Project created successfully",
            "project_id": project_id
        })
        
    except Exception as e:
        print(f"Error creating project: {e}")
        return jsonify({"error": str(e)}), 500
@app.route('/api/run-project-setup', methods=['POST'])
def run_project_setup():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        if not project_id: return jsonify({"error": "project_id required"}), 400
        
        # Fetch Project Details
        proj_res = supabase.table('projects').select('*').eq('id', project_id).execute()
        if not proj_res.data: return jsonify({"error": "Project not found"}), 404
        project = proj_res.data[0]
        domain = project['domain']
        
        print(f"Starting Setup for {domain}...")
        
        # 1. Research Business (The Brain)
        print("Starting Gemini research...")
        try:
            tools = [{'google_search': {}}]
            model = genai.GenerativeModel('gemini-2.0-flash-exp', tools=tools)
        except:
            print("Warning: Google Search tool failed. Using standard model.")
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        You are an expert business analyst. Research the website {domain} and create a comprehensive Business Profile.
        
        Context:
        - Language: {project.get('language')}
        - Location: {project.get('location')}
        - Focus: {project.get('focus')}
        
        I need you to find:
        1. Business Summary: What do they do? (1 paragraph)
        2. Ideal Customer Profile (ICP): Who are they selling to? Be specific.
        3. Brand Voice: How do they sound?
        4. Primary Products: List their main products/services.
        5. Competitors: List 3-5 potential competitors.
        6. Unique Selling Points (USPs): What makes them different?
        
        Return JSON:
        {{
            "business_summary": "...",
            "ideal_customer_profile": "...",
            "brand_voice": "...",
            "primary_products": ["..."],
            "competitors": ["..."],
            "unique_selling_points": ["..."]
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Parse JSON
        import json
        text = response.text.strip()
        if text.startswith('```json'): text = text[7:]
        if text.startswith('```'): text = text[3:]
        if text.endswith('```'): text = text[:-3]
        
        profile_data = json.loads(text.strip())
        
        # 2. Generate Content Strategy Plan
        print("Generating Strategy Plan...")
        strategy_prompt = f"""
        Based on this business profile:
        {json.dumps(profile_data)}
        
        Create a high-level Content Strategy Plan following the "Bottom-Up" approach:
        1. Bottom Funnel (BoFu): What product/service pages need optimization?
        2. Middle Funnel (MoFu): What comparison/best-of topics link to BoFu?
        3. Top Funnel (ToFu): What informational topics link to MoFu?
        
        Return a short markdown summary of the strategy.
        """
        strategy_res = model.generate_content(strategy_prompt)
        strategy_plan = strategy_res.text
        
        # Save Business Profile
        # WORKAROUND: Append Strategy Plan to Business Summary for persistence
        combined_summary = profile_data.get("business_summary", "")
        if strategy_plan:
            combined_summary += "\n\n===STRATEGY_PLAN===\n\n" + strategy_plan

        profile_insert = {
            "project_id": project_id,
            "business_summary": combined_summary,
            "ideal_customer_profile": profile_data.get("ideal_customer_profile"),
            "brand_voice": profile_data.get("brand_voice"),
            "primary_products": profile_data.get("primary_products"),
            "competitors": profile_data.get("competitors"),
            "unique_selling_points": profile_data.get("unique_selling_points")
        }
        
        # Check if exists, update or insert
        existing = supabase.table('business_profiles').select('id').eq('project_id', project_id).execute()
        if existing.data:
            supabase.table('business_profiles').update(profile_insert).eq('id', existing.data[0]['id']).execute()
        else:
            supabase.table('business_profiles').insert(profile_insert).execute()

        # 3. Crawl Sitemap (The Map)
        do_audit = data.get('do_audit', False)
        pages_to_insert = []
        
        if do_audit:
            print("Starting sitemap crawl (Audit enabled)...")
            pages_to_insert = crawl_sitemap(domain, project_id)
            
            if pages_to_insert:
                print(f"Found {len(pages_to_insert)} pages. syncing with DB...")
                
                # 1. Get existing URLs to avoid duplicates
                existing_res = supabase.table('pages').select('url, id, tech_audit_data').eq('project_id', project_id).execute()
                existing_map = {row['url']: row for row in existing_res.data}
                
                new_pages = []
                
                for p in pages_to_insert:
                    url = p['url']
                    if url in existing_map:
                        # Update existing page if title is missing or we have a better one
                        existing_row = existing_map[url]
                        existing_data = existing_row.get('tech_audit_data') or {}
                        new_data = p.get('tech_audit_data') or {}
                        
                        # If existing has no title, or we want to refresh it
                        if not existing_data.get('title') or new_data.get('title') != 'Untitled Product':
                            # Merge data
                            updated_data = existing_data.copy()
                            updated_data.update(new_data)
                            
                            # Only update if changed
                            if updated_data != existing_data:
                                print(f"Updating title for {url}")
                                supabase.table('pages').update({'tech_audit_data': updated_data}).eq('id', existing_row['id']).execute()
                    else:
                        new_pages.append(p)
                
                # 2. Insert only new pages
                if new_pages:
                    print(f"Inserting {len(new_pages)} new pages...")
                    batch_size = 100
                    for i in range(0, len(new_pages), batch_size):
                        batch = new_pages[i:i+batch_size]
                        supabase.table('pages').insert(batch).execute()
        else:
            print("Audit disabled. Skipping crawl.")
                
        return jsonify({
            "message": "Project setup complete",
            "profile": profile_insert,
            "strategy_plan": strategy_plan,
            "pages_found": len(pages_to_insert),
            "audit_run": do_audit
        })

    except Exception as e:
        print(f"Error in run_project_setup: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-funnel', methods=['POST'])
def generate_funnel():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
        
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        project_id = data.get('project_id')
        current_stage = data.get('current_stage', 'BoFu') # Default to BoFu if not sent
        
        if not page_id or not project_id:
            return jsonify({"error": "page_id and project_id are required"}), 400
            
        # 1. Fetch Context
        profile_res = supabase.table('business_profiles').select('*').eq('project_id', project_id).execute()
        profile = profile_res.data[0] if profile_res.data else {}
        
        page_res = supabase.table('pages').select('*').eq('id', page_id).execute()
        page = page_res.data[0] if page_res.data else {}
        
        target_stage = "MoFu" if current_stage == 'BoFu' else "ToFu"
        
        print(f"Generating {target_stage} strategy for {page.get('url')}...")
        
        # 2. Prompt Gemini
        prompt = f"""
        You are a strategic SEO expert for this business:
        Summary: {profile.get('business_summary')}
        ICP: {profile.get('ideal_customer_profile')}
        
        We are building a Content Funnel.
        Current Page ({current_stage}): {page.get('title')} ({page.get('url')})
        
        Task: Generate 5 high-impact "{target_stage}" content ideas that will drive traffic to this Current Page.
        
        Definitions:
        - If Target is MoFu (Middle of Funnel): Generate "Comparison", "Best X for Y", or "Alternative to Z" articles. These help users evaluate options.
        - If Target is ToFu (Top of Funnel): Generate "How-to", "What is", or "Guide" articles. These help users understand the problem.
        
        Output JSON format:
        [
            {{
                "topic_title": "Title of the article",
                "primary_keyword": "Main SEO keyword",
                "rationale": "Why this drives traffic to the parent page"
            }}
        ]
        """
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        
        # 3. Parse and Save
        ideas = json.loads(response.text)
        
        # 4. Enrich with DataForSEO (Optional)
        try:
            keywords = [idea.get('primary_keyword') for idea in ideas if idea.get('primary_keyword')]
            keyword_data = fetch_keyword_data(keywords)
        except Exception as e:
            print(f"DataForSEO Error: {e}")
            keyword_data = {}

        briefs_to_insert = []
        for idea in ideas:
            kw = idea.get('primary_keyword')
            data = keyword_data.get(kw, {})
            
            briefs_to_insert.append({
                "project_id": project_id,
                "topic_title": idea.get('topic_title'),
                "primary_keyword": kw,
                "rationale": idea.get('rationale'),
                "parent_page_id": page_id, 
                "status": "Proposed",
                "funnel_stage": target_stage,
                "meta_data": data # Store volume/kd here
            })
            
        if briefs_to_insert:
            supabase.table('content_briefs').insert(briefs_to_insert).execute()
            
        return jsonify({
            "message": f"Generated {len(briefs_to_insert)} {target_stage} ideas",
            "ideas": briefs_to_insert
        })

    except Exception as e:
        print(f"Error in generate_funnel: {e}")
        return jsonify({"error": str(e)}), 500

def fetch_keyword_data(keywords):
    if not keywords: 
        print("No keywords provided to fetch_keyword_data")
        return {}
    
    login = os.environ.get('DATAFORSEO_LOGIN')
    password = os.environ.get('DATAFORSEO_PASSWORD')
    
    print(f"DataForSEO Login: {login}, Password: {'*' * len(password) if password else 'None'}")
    
    if not login or not password:
        print("DataForSEO credentials missing")
        return {}
        
    url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_ideas/live"
    
    # We can use 'keyword_ideas' or 'keywords_for_site' or just 'search_volume'
    # 'search_volume' is best for specific lists.
    url = "https://api.dataforseo.com/v3/dataforseo_labs/google/historical_search_volume/live"
    
    payload = [{
        "keywords": keywords,
        "location_code": 2840, # US
        "language_code": "en"
    }]
    
    try:
        print(f"Fetching keyword data for {len(keywords)} keywords: {keywords[:3]}...")
        response = requests.post(url, auth=(login, password), json=payload)
        res_data = response.json()
        
        print(f"DataForSEO Response Status: {response.status_code}")
        print(f"DataForSEO Response: {res_data}")
        
        result = {}
        if res_data.get('tasks') and len(res_data['tasks']) > 0:
            task_result = res_data['tasks'][0].get('result')
            if task_result:
                for item in task_result:
                    kw = item.get('keyword')
                    vol = item.get('search_volume', 0)
                    result[kw] = {"volume": vol}
                    print(f"Keyword '{kw}': Volume = {vol}")
            else:
                print("No result in task")
        else:
            print("No tasks in response")
                
        return result
        
    except Exception as e:
        print(f"DataForSEO Request Failed: {e}")
        import traceback
        traceback.print_exc()
        return {}


@app.route('/api/auto-classify', methods=['POST'])
def auto_classify():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
        
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        
        # 1. Fetch Unclassified Pages
        # Note: Supabase 'is' filter for null might be .is_('funnel_stage', 'null') or similar.
        # Simpler to fetch all and filter in python if dataset is small, or use 'eq' for 'Unclassified'.
        # Let's assume we default to 'Unclassified' string.
        pages_res = supabase.table('pages').select('id, url, title').eq('project_id', project_id).execute()
        all_pages = pages_res.data
        
        # Filter for unclassified or null
        unclassified = [p for p in all_pages if not p.get('funnel_stage') or p.get('funnel_stage') == 'Unclassified']
        
        if not unclassified:
            return jsonify({"message": "No unclassified pages found."})
            
        # Limit to 50 for now to avoid timeouts
        batch = unclassified[:50]
        
        # 2. Fetch Profile
        profile_res = supabase.table('business_profiles').select('*').eq('project_id', project_id).execute()
        profile = profile_res.data[0] if profile_res.data else {}
        
        print(f"Auto-classifying {len(batch)} pages...")
        
        # 3. Prompt Gemini
        urls_list = "\n".join([f"- ID: {p['id']}, URL: {p['url']}, Title: {p.get('title', '')}" for p in batch])
        
        prompt = f"""
        You are an SEO Site Auditor.
        Business: {profile.get('business_summary')}
        
        Task: Classify the following pages into their Funnel Stage.
        
        Categories:
        - BoFu (Bottom of Funnel): Product pages, Pricing, Sign up, "Book a Demo", specific feature pages. (High conversion intent).
        - MoFu (Middle of Funnel): Case studies, Comparisons, "Best X Tools", Whitepapers. (Evaluation intent).
        - ToFu (Top of Funnel): Blog posts, Guides, "What is X", Definitions. (Learning intent).
        - Ignore: Login, Terms of Service, Privacy Policy, 404, generic contact pages.
        
        Pages to Classify:
        {urls_list}
        
        Output JSON format:
        [
            {{ "id": "page_id", "stage": "BoFu" }},
            ...
        ]
        """
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        
        # Clean JSON
        text = response.text.strip()
        if text.startswith('```json'): text = text[7:]
        if text.startswith('```'): text = text[3:]
        if text.endswith('```'): text = text[:-3]
        
        classification = json.loads(text.strip())
        
        # 4. Update DB
        count = 0
        for item in classification:
            stage = item.get('stage')
            pid = item.get('id')
            if stage and pid:
                supabase.table('pages').update({'funnel_stage': stage}).eq('id', pid).execute()
                count += 1
                
        return jsonify({"message": f"Classified {count} pages."})

    except Exception as e:
        print(f"Error in auto_classify: {e}")
        return jsonify({"error": str(e)}), 500



import uuid # Added for filename generation

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        try:
            # Read file data
            file_data = file.read()
            filename = f"{uuid.uuid4()}_{file.filename}"
            
            # Upload to Supabase
            public_url = upload_to_supabase(file_data, filename)
            
            return jsonify({"url": public_url})
        except Exception as e:
            print(f"Upload error: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image_endpoint():
    data = request.json
    prompt = data.get('prompt')
    input_image_url = data.get('input_image_url')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        # 1. Enhance Prompt using Gemini (Text)
        # We can use the new client for this too, or stick to old one. 
        # Let's use the new client for consistency if possible, but mixing is fine for now to minimize risk.
        # Actually, let's just use the new client for image gen as tested.
        
        enhanced_prompt = prompt 
        # (Optional: Add enhancement logic back if needed, but for now direct is fine or we can re-add it)
        # The previous code used `model = genai.GenerativeModel("gemini-2.0-flash-exp")` from old SDK.
        # Let's keep the enhancement logic using the old SDK if it works, or switch to new.
        # To avoid conflict, let's just use the prompt directly for now to ensure image gen works, 
        # or use the new client for text generation too.
        
        # Let's use the new client for image generation.
        from google import genai
        from google.genai import types
        import base64
        
        # Assuming GEMINI_API_KEY is set as an environment variable or globally
        GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
        if not GEMINI_API_KEY:
            return jsonify({"error": "GEMINI_API_KEY not configured"}), 500

        client = genai.Client(api_key=GEMINI_API_KEY)
        
        print(f"Generating image for prompt: {prompt}")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9"
                )
            )
        )
        
        UPLOAD_FOLDER = os.path.join('public', 'uploads')
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        output_filename = f"gen_{uuid.uuid4()}.png"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        image_saved = False
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    data = part.inline_data.data
                    if isinstance(data, str):
                        image_data = base64.b64decode(data)
                    else:
                        image_data = data
                        
                    with open(output_path, "wb") as f:
                        f.write(image_data)
                    image_saved = True
                    break
        
        if not image_saved:
            return jsonify({'error': 'No image generated'}), 500

        # Return URL
        output_url = f"/uploads/{output_filename}"
        
        return jsonify({
            'output_image_url': output_url,
            'status': 'Done',
            'enhanced_prompt': prompt 
        })

    except Exception as e:
        print(f"Error generating image: {e}")
        return jsonify({'error': str(e)}), 500







@app.route('/api/write-article-v2', methods=['POST'])
def write_article_v2():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
        
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        topic = data.get('topic')
        keyword = data.get('keyword')
        parent_page_id = data.get('parent_page_id') # The BoFu page to link to
        
        if not project_id or not topic:
            return jsonify({"error": "project_id and topic are required"}), 400
        
        # 1. Fetch Context
        profile_res = supabase.table('business_profiles').select('*').eq('project_id', project_id).execute()
        profile = profile_res.data[0] if profile_res.data else {}
        
        parent_page = {}
        if parent_page_id:
            page_res = supabase.table('pages').select('*').eq('id', parent_page_id).execute()
            parent_page = page_res.data[0] if page_res.data else {}
            
        print(f"Writing article '{topic}' for project {project_id}...")
            
        # 2. Construct Prompt
        prompt = f"""
        You are a professional content writer for this business:
        Summary: {profile.get('business_summary')}
        ICP: {profile.get('ideal_customer_profile')}
        Voice: {profile.get('brand_voice')}
        
        Task: Write a high-quality, SEO-optimized article.
        Title: {topic}
        Primary Keyword: {keyword}
        
        CRITICAL INSTRUCTION - INTERNAL LINKING:
        You MUST include a natural, persuasive link to our product page within the content.
        Product Page URL: {parent_page.get('url')}
        Product Name: {parent_page.get('title', 'our product')}
        
        The link should not be "Click here". It should be contextual, e.g., "For the best solution, check out [Product Name]." or "Many experts recommend [Product Name] for this."
        
        Format: Markdown.
        Structure:
        - H1 Title
        - Introduction (Hook the ICP)
        - Body Paragraphs (H2s and H3s)
        - Conclusion
        """
        
        # 3. Generate
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        content = response.text
        
        # Return content ONLY (No auto-save)
        return jsonify({
            "content": content,
            "meta": {
                "linked_to": parent_page.get('url')
            }
        })

    except Exception as e:
        print(f"Error in write_article_v2: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/save-article', methods=['POST'])
def save_article():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        data = request.get_json()
        print(f"Saving article: {data.get('topic')} for project {data.get('project_id')}")
        
        project_id = data.get('project_id')
        topic = data.get('topic')
        content = data.get('content')
        keyword = data.get('keyword')
        parent_page_id = data.get('parent_page_id')
        
        # Check if brief exists
        existing = supabase.table('content_briefs').select('id').eq('project_id', project_id).eq('topic_title', topic).execute()
        
        if existing.data:
            print(f"Updating existing brief: {existing.data[0]['id']}")
            # Update
            brief_id = existing.data[0]['id']
            supabase.table('content_briefs').update({
                'content_markdown': content,
                'status': 'Draft'
            }).eq('id', brief_id).execute()
        else:
            print("Inserting new brief")
            # Insert new
            supabase.table('content_briefs').insert({
                'project_id': project_id,
                'topic_title': topic,
                'primary_keyword': keyword,
                'parent_page_id': parent_page_id,
                'content_markdown': content,
                'status': 'Draft',
                'funnel_stage': 'MoFu'
            }).execute()
            
        return jsonify({"message": "Article saved successfully"})
    except Exception as e:
        print(f"Error saving article: {e}")
        return jsonify({"error": str(e)}), 500

# ... (generate_image and crawl_project remain unchanged) ...

@app.route('/api/get-articles', methods=['GET'])
def get_articles():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    project_id = request.args.get('project_id')
    if not project_id: return jsonify({"error": "project_id required"}), 400
    
    try:
        print(f"Fetching articles for project: {project_id}")
        res = supabase.table('content_briefs').select('*').eq('project_id', project_id).in_('status', ['Draft', 'Published']).execute()
        print(f"Found {len(res.data)} articles")
        return jsonify({"articles": res.data})
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return jsonify({"error": str(e)}), 500

import time
import os

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        
        print(f"Generating image with Gemini 2.5 Flash Image for prompt: {prompt[:100]}...")
        
        # Use Gemini 2.5 Flash Image model as requested
        model = genai.GenerativeModel('gemini-2.5-flash-image')
        
        response = model.generate_content(prompt)
        
        # Check if we have a valid response
        if not response or not response.parts:
            raise Exception("No content returned from image generation model")

        for part in response.parts:
            if hasattr(part, 'inline_data'):
                print("Found inline_data in response!")
                import base64
                from PIL import Image
                import io
                
                # Decode base64 image
                image_data = base64.b64decode(part.inline_data.data)
                image = Image.open(io.BytesIO(image_data))
                
                # Ensure directory exists
                output_dir = os.path.join(os.getcwd(), 'public', 'generated_images')
                os.makedirs(output_dir, exist_ok=True)
                
                filename = f"img_{int(time.time())}.png"
                filepath = os.path.join(output_dir, filename)
                
                # Save the image
                image.save(filepath, 'PNG')
                
                print(f"Image saved to: {filepath}")
                
                # Return URL relative to public root
                return jsonify({"image_url": f"/generated_images/{filename}"})
        
        # If we get here, no image was found in parts
        print(f"No image found in response parts. Response text: {response.text if hasattr(response, 'text') else 'No text'}")
        raise Exception("Model returned content but no image data found.")

    except Exception as e:
        error_msg = f"Image generation failed: {str(e)}"
        print(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/api/crawl-project', methods=['POST'])
def crawl_project_endpoint():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
        
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
            
        # Fetch domain from project
        project_res = supabase.table('projects').select('domain').eq('id', project_id).execute()
        if not project_res.data:
            return jsonify({"error": "Project not found"}), 404
            
        domain = project_res.data[0]['domain']
        
        print(f"Re-crawling project {project_id} ({domain})...")
        pages = crawl_sitemap(domain, project_id)
        
        if pages:
            supabase.table('pages').insert(pages).execute()
            
        return jsonify({
            "message": f"Crawl complete. Found {len(pages)} pages.",
            "pages_found": len(pages)
        })
    except Exception as e:
        print(f"Error crawling project: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/batch-update-pages', methods=['POST'])
def batch_update_pages():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        data = request.get_json()
        page_ids = data.get('page_ids', [])
        action = data.get('action')
        
        if not page_ids or not action:
            return jsonify({"error": "page_ids and action required"}), 400
            
        if action == 'trigger_audit':
            # In a real app, this would trigger a background job
            supabase.table('pages').update({"audit_status": "Pending"}).in_('id', page_ids).execute()
            
        elif action == 'trigger_classification':
            supabase.table('pages').update({"classification_status": "Pending"}).in_('id', page_ids).execute()
            
        elif action == 'approve_strategy':
            supabase.table('pages').update({"approval_status": True}).in_('id', page_ids).execute()
            
        elif action == 'scrape_content':
            # Scrape existing content for selected pages
            for page_id in page_ids:
                page_res = supabase.table('pages').select('*').eq('id', page_id).single().execute()
                if not page_res.data: continue
                page = page_res.data
                
                try:
                    import requests
                    from bs4 import BeautifulSoup
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    }
                    response = requests.get(page['url'], headers=headers, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Remove unwanted elements BEFORE extraction
                        for unwanted in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
                            unwanted.decompose()
                        
                        # Also remove common navigation/menu classes
                        for element in soup.find_all(class_=lambda x: x and any(term in str(x).lower() for term in ['nav', 'menu', 'sidebar', 'breadcrumb', 'footer', 'header'])):
                            element.decompose()
                        
                        # Extract main content
                        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'main-content', 'post-content', 'entry-content', 'article-content'])
                        
                        if main_content:
                            # Get paragraphs and headings only (skip lists that might be menus)
                            content_parts = []
                            for elem in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote']):
                                text = elem.get_text(strip=True)
                                if text and len(text) > 20:  # Only include substantial text
                                    content_parts.append(text)
                            body_content = '\n\n'.join(content_parts)
                        else:
                            # Fallback: get all paragraphs
                            paragraphs = soup.find_all('p')
                            content_parts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20]
                            body_content = '\n\n'.join(content_parts) if content_parts else "Could not extract meaningful content"
                        
                        # Final cleanup
                        body_content = body_content.strip()
                        
                        # Update tech_audit_data with body_content
                        current_tech_data = page.get('tech_audit_data', {})
                        current_tech_data['body_content'] = body_content
                        
                        supabase.table('pages').update({
                            "tech_audit_data": current_tech_data
                        }).eq('id', page_id).execute()
                        
                        print(f"✓ Scraped content for {page['url']}")
                except Exception as e:
                    print(f"✗ Error scraping {page['url']}: {e}")
            
        elif action == 'generate_content':
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            for page_id in page_ids:
                # 1. Get Page Data
                page_res = supabase.table('pages').select('*').eq('id', page_id).single().execute()
                if not page_res.data: continue
                page = page_res.data
                
                # 2. Get existing content
                existing_content = page.get('tech_audit_data', {}).get('body_content', '')
                if not existing_content:
                    # If no body content, try to scrape it now
                    try:
                        import requests
                        from bs4 import BeautifulSoup
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                        }
                        response = requests.get(page['url'], headers=headers, timeout=15)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'main-content', 'post-content'])
                            if main_content:
                                existing_content = main_content.get_text(separator='\n', strip=True)
                            else:
                                body = soup.find('body')
                                if body:
                                    for script in body(["script", "style", "nav", "footer", "header"]):
                                        script.decompose()
                                    existing_content = body.get_text(separator='\n', strip=True)
                    except Exception as e:
                        print(f"Error scraping content for {page['url']}: {e}")
                        existing_content = "No content available"
                
                # 3. Generate improved content
                page_title = page.get('tech_audit_data', {}).get('title', page.get('url', ''))
                page_type = page.get('page_type', 'page')
                
                try:
                    prompt = f"""You are an expert SEO content strategist and writer specializing in data-driven content optimization.

**TASK**: Analyze and significantly improve the existing content for this {page_type} page while maintaining factual accuracy.

**PAGE DETAILS**:
- URL: {page['url']}
- Title: {page_title}
- Page Type: {page_type}

**EXISTING CONTENT** (use as foundation, preserve all facts):
```
{existing_content[:5000]}
```

**COMPREHENSIVE IMPROVEMENT REQUIREMENTS**:

1. **Preserve Accuracy**: Keep ALL factual information, data points, statistics, and specific claims from the original
2. **Add Value**: Enhance with:
   - Relevant 2025 industry trends and statistics
   - Best practices and expert insights
   - Actionable tips and examples
   - Data-backed recommendations

3. **SEO Optimization**:
   - Natural keyword integration (analyze title/URL for primary keywords)
   - Strategic use of semantic keywords
   - Optimized heading structure (H2, H3)
   - Internal linking opportunities (mention relevant topics)
   - Meta description (compelling, 150-160 chars)

4. **Content Structure**:
   - Clear, scannable hierarchy
   - Bullet points for lists
   - Short paragraphs (2-3 sentences)
   - Subheadings every 200-300 words
   - Table of contents if content > 1000 words

5. **Quality Standards**:
   - Engaging, conversational tone
   - Active voice preferred
   - No fluff or generic statements
   - Specific, actionable information
   - Proper markdown formatting

**OUTPUT FORMAT** (strict):
```markdown
**Meta Description**: [150-160 char compelling description]

# [Optimized H1 Title]

[Hook paragraph - 2-3 sentences]

## [First Major Section - H2]

[Content with data/examples]

### [Subsection - H3]
...
```

Return ONLY the improved markdown content. Start with the meta description block."""

                    response = model.generate_content(prompt)
                    new_content = response.text.strip()
                    
                    # Extract Meta Description
                    meta_desc = None
                    import re
                    match = re.search(r'\*\*Meta Description\*\*:\s*(.*?)(?:\n|$)', new_content)
                    if match:
                        meta_desc = match.group(1).strip()
                    
                    # Update tech_audit_data with new meta description
                    current_tech_data = page.get('tech_audit_data') or {}
                    if meta_desc:
                        current_tech_data['meta_description'] = meta_desc
                    
                    # 4. Update DB
                    supabase.table('pages').update({
                        "content": new_content,
                        "product_action": "Idle", # Reset action
                        "tech_audit_data": current_tech_data
                    }).eq('id', page_id).execute()
                    
                    print(f"✓ Generated improved content for {page['url']}")
                except Exception as gen_error:
                    print(f"✗ Error generating content for {page['url']}: {gen_error}")
        elif action == 'generate_mofu':
            # AI MoFu Topic Generation
            # Use Gemini 2.0 Flash Exp with Google Search for Deep Research
            try:
                tools = [{'google_search': {}}]
                model = genai.GenerativeModel('gemini-2.0-flash-exp', tools=tools)
            except:
                print("Warning: Google Search tool failed. Using standard model.")
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            for pid in page_ids:
                # Fetch Source Product Page
                product_res = supabase.table('pages').select('*').eq('id', pid).single().execute()
                if not product_res.data: continue
                product = product_res.data
                product_tech = product.get('tech_audit_data') or {}
                
                print(f"Researching MoFu opportunities for {product.get('url')}...")
                
                # Step 1: Deep Research (Competitors, Gaps, Keywords)
                research_prompt = f"""
                You are a Senior SEO Strategist. Conduct EXHAUSTIVE, DEEP-DIVE research for this product to identify Middle-of-Funnel (MoFu) content opportunities.
                
                Product: {product.get('url')}
                Title: {product_tech.get('title')}
                
                Research Goals (BE DETAILED):
                1. **Competitor Landscape**: Identify 3-5 direct competitors. Analyze their MoFu content (Comparison pages, "Best of" lists). What are their strengths and weaknesses?
                2. **Content Gap Analysis**: What questions are users asking that competitors aren't answering well? Look for forum discussions (Reddit, Quora) or "People Also Ask".
                3. **Keyword Opportunities**: Identify "High Intent" keywords.
                4. **Unique Value Proposition**: How can we position this product as superior in a comparison?
                
                Output JSON:
                {{
                    "competitor_analysis": "Detailed analysis of competitors A, B, C...",
                    "content_gaps": ["Detailed gap 1...", "Detailed gap 2..."],
                    "key_insights": ["Insight 1...", "Insight 2..."],
                    "search_intent": "Comprehensive analysis of what users are looking for when comparing...",
                    "market_positioning": "Strategy for positioning against competitors..."
                }}
                """
                
                try:
                    research_res = model.generate_content(research_prompt)
                    research_text = research_res.text.strip()
                    if research_text.startswith('```json'): research_text = research_text[7:]
                    if research_text.startswith('```'): research_text = research_text[3:]
                    if research_text.endswith('```'): research_text = research_text[:-3]
                    research_data = json.loads(research_text)
                except Exception as e:
                    print(f"Research failed: {e}")
                    research_data = {"brief": "Research failed, using fallback."}

                # Step 2: Generate Topics based on Research
                import datetime
                current_year = datetime.datetime.now().year
                next_year = current_year + 1
                
                topic_prompt = f"""
                Based on this research:
                {json.dumps(research_data)}
                
                Generate 6 High-Value Middle-of-Funnel (MoFu) topic ideas for the product: {product.get('url')}
                
                Current Date: {datetime.datetime.now().strftime("%B %Y")}
                IMPORTANT: For any "Best of" or time-sensitive titles, use the year {current_year} or {next_year}. NEVER use older years like 2024.
                
                Focus on:
                - "Vs" comparisons (Product vs Competitor)
                - "Best" lists (Best X for Y in {current_year})
                - "Alternatives" (Top Alternatives to Competitor)
                - In-depth Use Cases
                
                Return JSON with key "topics":
                [
                    {{
                        "title": "Topic Title",
                        "slug": "url-slug",
                        "description": "Brief content description",
                        "keywords": "target, keywords, comma, separated",
                        "research_brief": "Specific research notes for this topic (why we chose it)"
                    }}
                ]
                """
                
                try:
                    response = model.generate_content(topic_prompt)
                    text = response.text.strip()
                    if text.startswith('```json'): text = text[7:]
                    if text.startswith('```'): text = text[3:]
                    if text.endswith('```'): text = text[:-3]
                    
                    data = json.loads(text)
                    topics = data.get('topics', [])
                    
                    new_pages = []
                    for t in topics:
                        # Combine general research with topic-specific brief
                        topic_research = research_data.copy()
                        topic_research['brief'] = t.get('research_brief', '')
                        
                        new_pages.append({
                            "project_id": product['project_id'],
                            "source_page_id": pid,
                            "url": f"{product['url'].rstrip('/')}/{t['slug']}",
                            "page_type": "Topic",
                            "funnel_stage": "MoFu",
                            "product_action": "Idle",
                            "tech_audit_data": {
                                "title": t['title'],
                                "meta_description": t['description'],
                                "meta_title": t['title']
                            },
                            "content_description": t['description'],
                            "keywords": t['keywords'],
                            "slug": t['slug'],
                            "research_data": topic_research # Store the deep research here!
                        })
                    
                    if new_pages:
                        print(f"Attempting to insert {len(new_pages)} MoFu topics...")
                        try:
                            supabase.table('pages').insert(new_pages).execute()
                            print("✓ MoFu topics inserted successfully.")
                        except Exception as insert_error:
                            print(f"Error inserting with research_data: {insert_error}")
                            # Fallback: Try inserting without research_data (if column missing)
                            if 'research_data' in str(insert_error) or 'column' in str(insert_error):
                                print("Retrying insert without research_data column...")
                                for p in new_pages:
                                    p.pop('research_data', None)
                                supabase.table('pages').insert(new_pages).execute()
                                print("✓ MoFu topics inserted (without research data).")
                            else:
                                raise insert_error
                    
                    # Update Source Page Status
                    supabase.table('pages').update({"product_action": "MoFu Generated"}).eq('id', pid).execute()
                    
                except Exception as e:
                    print(f"Error generating MoFu topics: {e}")
                    import traceback
                    traceback.print_exc()

        elif action == 'generate_tofu':
            # AI ToFu Topic Generation
            # Use Gemini 2.0 Flash Exp with Google Search for Deep Research
            try:
                tools = [{'google_search': {}}]
                model = genai.GenerativeModel('gemini-2.0-flash-exp', tools=tools)
            except:
                print("Warning: Google Search tool failed. Using standard model.")
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            for pid in page_ids:
                # Fetch Source MoFu Page
                mofu_res = supabase.table('pages').select('*').eq('id', pid).single().execute()
                if not mofu_res.data: continue
                mofu = mofu_res.data
                mofu_tech = mofu.get('tech_audit_data') or {}
                
                print(f"Researching ToFu opportunities for MoFu topic: {mofu_tech.get('title')}...")
                
                # Step 1: Deep Research (User Questions, Pain Points)
                research_prompt = f"""
                You are a Senior Content Strategist. Conduct EXHAUSTIVE, DEEP-DIVE research to identify Top-of-Funnel (ToFu) content opportunities that lead to this Middle-of-Funnel (MoFu) topic.
                
                MoFu Topic: {mofu_tech.get('title')}
                MoFu Context: {mofu.get('content_description')}
                
                Research Goals (BE DETAILED):
                1. **User Persona Deep Dive**: Who is the user? What are their fears, frustrations, and desires BEFORE they know about the solution?
                2. **Problem Analysis**: What specific problems are they facing? (e.g., "Why is my skin breaking out?", "Sunscreen makes me oily").
                3. **Competitor Content Gap**: What are competitors writing about? What are they MISSING? Where can we add more value?
                4. **SERP Analysis**: What types of content are ranking? (Guides, Videos, Lists).
                
                Output JSON:
                {{
                    "user_questions": ["Detailed question 1", "Detailed question 2", ...],
                    "educational_gaps": ["Detailed gap analysis 1...", "Detailed gap analysis 2..."],
                    "key_insights": ["Insight 1 (with stats if found)...", "Insight 2..."],
                    "search_intent": "Comprehensive analysis of user intent, psychological state, and buying readiness...",
                    "competitor_analysis": "Detailed breakdown of top 3 competitors and their content weaknesses..."
                }}
                """
                
                try:
                    research_res = model.generate_content(research_prompt)
                    research_text = research_res.text.strip()
                    if research_text.startswith('```json'): research_text = research_text[7:]
                    if research_text.startswith('```'): research_text = research_text[3:]
                    if research_text.endswith('```'): research_text = research_text[:-3]
                    research_data = json.loads(research_text)
                except Exception as e:
                    print(f"ToFu Research failed: {e}")
                    research_data = {"brief": "Research failed, using fallback."}

                # Step 2: Generate Topics based on Research
                import datetime
                current_year = datetime.datetime.now().year
                
                topic_prompt = f"""
                Based on this research:
                {json.dumps(research_data)}
                
                Generate 5 High-Value Top-of-Funnel (ToFu) topic ideas that lead to: {mofu_tech.get('title')}
                
                Current Date: {datetime.datetime.now().strftime("%B %Y")}
                IMPORTANT: Use year {current_year} where relevant.
                
                ToFu Goal: Create broad, educational, or problem-aware content that naturally leads people to the solution (the MoFu topic).
                Focus on "What is", "How to", "Guide to", "Benefits of" type content.
                
                Return a JSON object with a key "topics" containing a list of objects.
                Each object must have:
                - "title": Topic Title
                - "slug": URL friendly slug
                - "description": Brief content description (intent)
                - "keywords": Comma separated target keywords
                - "research_brief": Specific research notes for this topic
                """
                
                try:
                    response = model.generate_content(topic_prompt)
                    text = response.text.strip()
                    if text.startswith('```json'): text = text[7:]
                    if text.startswith('```'): text = text[3:]
                    if text.endswith('```'): text = text[:-3]
                    
                    data = json.loads(text)
                    topics = data.get('topics', [])
                    
                    new_pages = []
                    for t in topics:
                        # Combine general research with topic-specific brief
                        topic_research = research_data.copy()
                        topic_research['brief'] = t.get('research_brief', '')

                        new_pages.append({
                            "project_id": mofu['project_id'],
                            "source_page_id": pid, # Link to MoFu
                            "url": f"{mofu['url'].rsplit('/', 1)[0]}/{t['slug']}", # Sibling URL structure or nested? Usually ToFu is broader, but let's keep flat or sub-folder. Let's assume flat for now or same level.
                            # Actually, ToFu might be /blog/topic vs MoFu /product/comparison. 
                            # For now, let's just append slug to base url to avoid complex path logic, or just use a clean slug.
                            # Let's use a safe hypothetical URL.
                            "page_type": "Topic",
                            "funnel_stage": "ToFu",
                            "product_action": "Idle",
                            "tech_audit_data": {
                                "title": t['title'],
                                "meta_description": t['description'],
                                "meta_title": t['title']
                            },
                            "content_description": t['description'],
                            "keywords": t['keywords'],
                            "slug": t['slug'],
                            "research_data": topic_research
                        })
                    
                    if new_pages:
                        print(f"Attempting to insert {len(new_pages)} ToFu topics...")
                        try:
                            supabase.table('pages').insert(new_pages).execute()
                            print("✓ ToFu topics inserted successfully.")
                        except Exception as insert_error:
                             print(f"Error inserting ToFu: {insert_error}")
                             # Fallback
                             if 'research_data' in str(insert_error):
                                 for p in new_pages: p.pop('research_data', None)
                                 supabase.table('pages').insert(new_pages).execute()

                    # Update Source MoFu Page Status
                    supabase.table('pages').update({"product_action": "ToFu Generated"}).eq('id', pid).execute()
                    
                except Exception as e:
                    print(f"Error generating ToFu topics: {e}")
                    import traceback
                    traceback.print_exc()

        return jsonify({"message": f"Batch action {action} completed"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-page-details', methods=['GET'])
def get_page_details():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        page_id = request.args.get('page_id')
        if not page_id: return jsonify({"error": "page_id required"}), 400
        
        res = supabase.table('pages').select('*').eq('id', page_id).execute()
        if not res.data: return jsonify({"error": "Page not found"}), 404
        
        return jsonify(res.data[0])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        print(f"Error in crawl_project: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/classify-page', methods=['POST'])
def classify_page():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
        
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        stage = data.get('stage') # 'BoFu', 'MoFu', 'ToFu', 'Ignore'
        
        if not page_id or not stage:
            return jsonify({"error": "page_id and stage are required"}), 400
            
        supabase.table('pages').update({'funnel_stage': stage}).eq('id', page_id).execute()
        
        return jsonify({"message": f"Page classified as {stage}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/generate-image-prompt', methods=['POST'])
def generate_image_prompt():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        data = request.get_json()
        topic = data.get('topic')
        
        prompt = f"""
        You are an expert AI Art Director.
        Create a detailed, high-quality image generation prompt for a blog post titled: "{topic}".
        
        The style should be: "Modern, Minimalist, Tech-focused, 3D Render, High Resolution".
        
        Return ONLY the prompt text. No "Here is the prompt" or quotes.
        """
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        return jsonify({"prompt": response.text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/run-migration', methods=['POST'])
def run_migration():
    """Run the photoshoots migration SQL"""
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        # Read the SQL file
        with open('migration_photoshoots.sql', 'r') as f:
            sql = f.read()
            
        # Execute using Supabase RPC or direct SQL if possible
        # Since Supabase-py client doesn't support direct SQL execution easily without RPC,
        # we'll try to use the 'rpc' method if you have a 'exec_sql' function defined in Postgres
        # OR we can just assume the table exists for now and let the user run it in Supabase dashboard.
        
        # However, to be helpful, let's try to create the table using a raw query if the client supports it.
        # The supabase-py client is a wrapper around postgrest. It doesn't support raw SQL.
        # But we can try to use the 'psycopg2' connection if we had the connection string.
        
        # Since we failed to connect with psycopg2 earlier, we can't run it here either.
        
        return jsonify({"message": "Please run the migration_photoshoots.sql file in your Supabase SQL Editor."}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== PRODUCT PHOTOSHOOT ENDPOINTS =====

@app.route('/api/photoshoots', methods=['GET'])
def get_photoshoots():
    """Get all photoshoot tasks for a project"""
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        project_id = request.args.get('project_id')
        if not project_id:
            return jsonify({"error": "project_id required"}), 400
        
        # Fetch from photoshoots table
        res = supabase.table('photoshoots').select('*').eq('project_id', project_id).order('created_at', desc=True).execute()
        return jsonify({"photoshoots": res.data or []})
    except Exception as e:
        print(f"Error fetching photoshoots: {e}")
        return jsonify({"photoshoots": []})

@app.route('/api/photoshoots', methods=['POST'])
def create_photoshoot():
    """Create a new photoshoot task"""
    print("Received create_photoshoot request")
    if not supabase: 
        print("Supabase not configured")
        return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        data = request.get_json()
        print(f"Request data: {data}")
        project_id = data.get('project_id')
        prompt = data.get('prompt', '')
        
        if not project_id:
            return jsonify({"error": "project_id required"}), 400
        
        # Insert into database
        new_task = {
            'project_id': project_id,
            'prompt': prompt,
            'status': 'Pending',
            'output_image': None
        }
        
        print(f"Inserting task: {new_task}")
        res = supabase.table('photoshoots').insert(new_task).execute()
        print(f"Insert result: {res}")
        return jsonify({"photoshoot": res.data[0] if res.data else new_task})
    except Exception as e:
        print(f"Error creating photoshoot: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/photoshoots/<photoshoot_id>', methods=['PUT'])
def update_photoshoot(photoshoot_id):
    """Update a photoshoot task"""
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        data = request.get_json()
        action = data.get('action')
        
        # Allow updating any field passed in data, excluding 'action' and 'id'
        update_data = {k: v for k, v in data.items() if k not in ['action', 'id', 'project_id']}
        
        # If action is 'run', generate the image
        if action == 'run':


            print(f"Starting generation for task {photoshoot_id}")
            # Get the prompt from the database to be sure
            # Get the prompt and input_image from the database
            current_task = supabase.table('photoshoots').select('prompt, input_image').eq('id', photoshoot_id).execute()
            if not current_task.data:
                 return jsonify({"error": "Task not found"}), 404
                 
            task_data = current_task.data[0]
            prompt_text = task_data.get('prompt', '')
            input_image_url = task_data.get('input_image', '')
            
            if not prompt_text:
                return jsonify({"error": "Prompt is empty"}), 400
                
            # Update status to Processing
            supabase.table('photoshoots').update({'status': 'Processing'}).eq('id', photoshoot_id).execute()
            
            try:
                content_parts = [prompt_text]
                
                # Load input image if it exists
                if input_image_url:
                    try:
                        img = load_image_data(input_image_url)
                        content_parts.append(img)
                    except Exception as e:
                        print(f"Error loading input image: {e}")
                        # Continue without image or fail? Fail seems safer for user expectation
                        return jsonify({"error": f"Failed to load input image: {str(e)}"}), 400
                
                print(f"Generating image with prompt: {prompt_text} and image: {bool(input_image_url)}")
                # Generate image using Gemini model
                image_model = genai.GenerativeModel('gemini-2.5-flash-image')
                response = image_model.generate_content(content_parts)
                
                print("Generation response received")
                
                # Save image to Supabase
                filename = f"gen_{photoshoot_id}_{int(time.time())}.png"
                
                # Handle response data
                image_data = None
                if hasattr(response, 'parts'):
                    for part in response.parts:
                        if part.inline_data:
                            image_data = part.inline_data.data
                            break
                
                if not image_data and hasattr(response, 'candidates'):
                     # Fallback check
                     if response.candidates and response.candidates[0].content.parts:
                         image_data = response.candidates[0].content.parts[0].inline_data.data

                if not image_data:
                    raise Exception("No image data found in response")

                # Upload to Supabase
                public_url = upload_to_supabase(image_data, filename)
                print(f"Image saved to {public_url}")
                
                # Update database
                update_data['status'] = 'Done'
                update_data['output_image'] = public_url
                
            except Exception as img_error:
                print(f"Image generation error: {img_error}")
                traceback.print_exc()
                update_data['status'] = 'Failed'
                # Don't return error immediately, update status first

        elif action == 'upscale':
            print(f"Starting upscale for task {photoshoot_id}")
            
            # Get the output_image from the database
            current_task = supabase.table('photoshoots').select('output_image').eq('id', photoshoot_id).execute()
            if not current_task.data:
                 return jsonify({"error": "Task not found"}), 404
                 
            task_data = current_task.data[0]
            output_image_url = task_data.get('output_image', '')
            
            if not output_image_url:
                return jsonify({"error": "No output image to upscale"}), 400
                
            # Update status to Processing
            supabase.table('photoshoots').update({'status': 'Processing'}).eq('id', photoshoot_id).execute()
            
            try:
                # Load the output image
                print(f"Loading image for upscale from: {output_image_url}")
                img = load_image_data(output_image_url)
                
                upscale_prompt = "Generate a high resolution, 4k, highly detailed, photorealistic version of this image. Maintain the exact composition and details but improve quality and sharpness."
                
                content_parts = [upscale_prompt, img]
                
                print(f"Generating upscale...")
                # Generate image using Gemini model
                image_model = genai.GenerativeModel('gemini-2.5-flash-image')
                response = image_model.generate_content(content_parts)
                
                print("Upscale response received")
                
                # Save image to Supabase
                filename = f"enhanced_{photoshoot_id}_{int(time.time())}.png"
                
                # Handle response data
                image_data = None
                if hasattr(response, 'parts'):
                    for part in response.parts:
                        if part.inline_data:
                            image_data = part.inline_data.data
                            break
                
                if not image_data and hasattr(response, 'candidates'):
                     if response.candidates and response.candidates[0].content.parts:
                         image_data = response.candidates[0].content.parts[0].inline_data.data

                if not image_data:
                    raise Exception("No image data found in response")

                # Upload to Supabase
                public_url = upload_to_supabase(image_data, filename)
                print(f"Enhanced image saved to {public_url}")
                
                # Update database
                update_data['status'] = 'Done'
                update_data['enhanced_output'] = public_url
                
            except Exception as img_error:
                print(f"Upscale error: {img_error}")
                traceback.print_exc()
                update_data['status'] = 'Failed'
                
        # Update the task with final status
        if update_data: # Ensure there's data to update before executing
            res = supabase.table('photoshoots').update(update_data).eq('id', photoshoot_id).execute()
            return jsonify({"photoshoot": res.data[0] if res.data else {}})
        
        return jsonify({"message": "No updates"})
    except Exception as e:
        print(f"Error updating photoshoot: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/photoshoots/<photoshoot_id>', methods=['DELETE'])
def delete_photoshoot(photoshoot_id):
    """Delete a photoshoot task"""
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        supabase.table('photoshoots').delete().eq('id', photoshoot_id).execute()
        return jsonify({"message": "Deleted successfully"})
    except Exception as e:
        print(f"Error deleting photoshoot: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project and all associated data"""
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    
    try:
        # Delete the project (cascading should handle related data if configured in DB, 
        # otherwise we might need to delete related rows first. Assuming cascade for now or simple delete)
        supabase.table('projects').delete().eq('id', project_id).execute()
        return jsonify({"message": "Project deleted successfully"})
    except Exception as e:
        print(f"Error deleting project: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
