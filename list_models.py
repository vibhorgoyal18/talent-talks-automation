"""List available Gemini models using google.genai."""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Available Gemini models:")
print("=" * 60)

try:
    models = client.models.list()
    for model in models:
        print(f"✓ {model.name}")
        if hasattr(model, 'display_name'):
            print(f"  Display: {model.display_name}")
        print()
except Exception as e:
    print(f"Error listing models: {e}")

