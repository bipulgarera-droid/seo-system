import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv('/Users/bipul/Downloads/seo-saas-brain/.env')
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

print("Listing models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
