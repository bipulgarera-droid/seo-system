import google.generativeai as genai
import os

GEMINI_API_KEY = "AIzaSyDC9xRLV94VJB1LMy0ci7QNaFSP6fO5ZiU"
genai.configure(api_key=GEMINI_API_KEY)

try:
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
