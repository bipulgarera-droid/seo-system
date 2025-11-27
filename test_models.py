import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

models_to_test = [
    'gemini-2.5-flash-image',
    'gemini-3-pro-image-preview',
    'imagen-3.0-generate-001',
    'gemini-2.0-flash-exp'
]

for model_name in models_to_test:
    print(f"Testing {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("A small red ball")
        print(f"SUCCESS: {model_name}")
        if hasattr(response, 'parts'):
            for part in response.parts:
                if part.inline_data:
                    print("Response has IMAGE data")
                if part.text:
                    print(f"Response has TEXT data: {part.text[:50]}...")
        elif hasattr(response, 'text'):
             print(f"Response has TEXT data: {response.text[:50]}...")
        break
    except Exception as e:
        print(f"FAILED: {model_name} - {e}")
