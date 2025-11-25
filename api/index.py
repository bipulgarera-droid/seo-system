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
        
        # Handle URL: if key is missing OR value is None, use default
        target_url = job.get('url')
        if not target_url:
            target_url = 'example.com'
        
        # Step B: Lock (Update status to PROCESSING)
        supabase.table('audit_results').update({"status": "PROCESSING"}).eq('id', job_id).execute()
        
        # Step C: Work (Generate SEO audit)
        # Using gemini-2.5-flash as requested and verified
        model = genai.GenerativeModel('gemini-2.5-flash')
        # Use dynamic URL in prompt
        prompt = f"Analyze the SEO strategy for {target_url}."
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
