from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure Gemini
# Using the provided key as a fallback if the environment variable is not set
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDC9xRLV94VJB1LMy0ci7QNaFSP6fO5ZiU")
genai.configure(api_key=GEMINI_API_KEY)

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

if __name__ == '__main__':
    app.run()
