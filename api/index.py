from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from supabase import create_client, Client

app = Flask(__name__)

# Configure Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDC9xRLV94VJB1LMy0ci7QNaFSP6fO5ZiU")
genai.configure(api_key=GEMINI_API_KEY)

# Configure Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

@app.route('/')
def home():
    return 'SEO System Active - Version 1.0'

@app.route('/test-ai', methods=['POST'])
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

@app.route('/start-audit', methods=['POST'])
def start_audit():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500

    try:
        # Create a new row with status 'PENDING'
        data, count = supabase.table('audit_results').insert({"status": "PENDING"}).execute()
        
        # Return the ID of the newly created row
        if data and len(data[1]) > 0:
             # supabase-py v2 returns data as a tuple (data, count), where data[1] is the list of rows
             # Wait, checking supabase-py v2 response format. 
             # It usually returns a response object or a tuple depending on version. 
             # Let's assume standard v2: response.data
             # Actually, let's be safe and inspect the return. 
             # The execute() method returns a `APIResponse` object which has `data` attribute.
             # Let's correct the code to use the object attribute access if possible, or standard dict access.
             # Standard usage: response = supabase.table(...).insert(...).execute()
             # response.data is the list of inserted rows.
             pass
        
        # Let's rewrite this block to be cleaner and safer
        response = supabase.table('audit_results').insert({"status": "PENDING"}).execute()
        
        if response.data and len(response.data) > 0:
            new_id = response.data[0]['id']
            return jsonify({"id": new_id, "status": "PENDING"})
        else:
            return jsonify({"error": "Failed to create audit record"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
