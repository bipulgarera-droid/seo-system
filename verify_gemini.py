import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.environ.get("GEMINI_API_KEY")

def test_model(model_name):
    print(f"Testing {model_name}...", end=" ")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": API_KEY}
    data = {"contents": [{"parts": [{"text": "Reply with 'OK'"}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("✅ SUCCESS")
        else:
            print(f"❌ FAILED ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ CRASHED: {e}")

if __name__ == "__main__":
    test_model("gemini-2.5-flash") # Fast Brain
    test_model("gemini-2.5-pro")   # Smart Brain