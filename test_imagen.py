from google import genai
from google.genai import types
import base64
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

client = genai.Client(api_key=api_key)

# Choose your model: 'gemini-2.5-flash-image' or 'gemini-3-pro-image-preview'
MODEL_ID = "gemini-2.5-flash-image"

print(f"Generating image with {MODEL_ID}...")

try:
    response = client.models.generate_content(
        model=MODEL_ID,
        contents="A futuristic city with flying cars, cyberpunk style, 4k resolution",
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="16:9"
            )
        )
    )

    # Save the generated image
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                # The new SDK might return bytes directly or base64 string. 
                # User snippet suggests base64 decoding.
                # Let's check type first or just try user's way.
                # User code: image_data = base64.b64decode(part.inline_data.data)
                
                # Note: In the new SDK, part.inline_data.data might be bytes already if using some clients, 
                # but let's stick to the user's snippet which implies it needs decoding.
                # However, usually if it's 'bytes', we don't b64decode. 
                # Let's try to inspect it or just write it if it's bytes.
                
                data = part.inline_data.data
                
                # If data is string, decode it. If bytes, write directly.
                if isinstance(data, str):
                    image_data = base64.b64decode(data)
                else:
                    image_data = data
                    
                with open("generated_image.png", "wb") as f:
                    f.write(image_data)
                print("Image saved to generated_image.png")
    else:
        print("No candidates or parts returned.")

except Exception as e:
    print(f"Error: {e}")
