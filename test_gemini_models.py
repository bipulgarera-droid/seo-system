
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found")
    exit(1)

client = genai.Client(api_key=api_key)

try:
    print("Testing gemini-2.5-pro...")
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents="Hello, are you working?"
    )
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Error testing gemini-2.5-pro: {e}")

try:
    print("\nTesting gemini-2.0-flash-exp (fallback check)...")
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents="Hello, are you working?"
    )
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Error testing gemini-2.0-flash-exp: {e}")
