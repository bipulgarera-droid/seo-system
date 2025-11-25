from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv('.env.local')
load_dotenv()

app = Flask(__name__, static_folder='../public', static_url_path='/')
CORS(app, resources={r"/api/*": {"origins": "*"}})

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
    return app.send_static_file('index.html')

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
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500

    try:
        # Explicitly get the JSON data
        data = request.get_json()
        target_url = data.get('url') if data else None
        
        # Print for debugging
        print(f"DEBUG: Received URL: {target_url}")

        # Crucial: Include it in the Supabase insert
        insert_payload = {'status': 'PENDING', 'url': target_url}
        response = supabase.table('audit_results').insert(insert_payload).execute()
        
        if response.data and len(response.data) > 0:
            new_id = response.data[0]['id']
            return jsonify({"id": new_id, "status": "PENDING"})
        else:
            return jsonify({"error": "Failed to create audit record"}), 500

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

        url = "https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live"
        payload = [
            {
                "target": domain,
                "location_code": 2840, # US
                "language_code": "en",
                "filters": [
                    ["rank_absolute", ">=", 1],
                    "and",
                    ["rank_absolute", "<=", 10]
                ],
                "order_by": ["keyword_info.search_volume,desc"],
                "limit": 5
            }
        ]
        headers = {
            'content-type': 'application/json'
        }

        response = requests.post(url, json=payload, auth=(DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD), headers=headers)
        print(f"DEBUG: Status Code: {response.status_code}")
        print(f"DEBUG: Raw Response: {response.text}")
        
        response.raise_for_status()
        data = response.json()

        keywords = []
        if data['tasks'] and data['tasks'][0]['result']:
            for item in data['tasks'][0]['result'][0]['items']:
                keywords.append(f"{item['keyword_data']['keyword']} (Vol: {item['keyword_data']['keyword_info']['search_volume']})")
        
        return keywords

    except Exception as e:
        print(f"DEBUG: ERROR OCCURRED: {str(e)}")
        print(f"DataForSEO Error: {e}")
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

if __name__ == '__main__':
    app.run()
