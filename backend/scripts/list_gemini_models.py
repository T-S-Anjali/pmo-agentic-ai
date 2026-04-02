import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not set in environment.")

# This endpoint may change; check Google GenAI docs if it fails.
url = "https://generativelanguage.googleapis.com/v1beta/models?key=" + API_KEY

response = requests.get(url, verify=False)
if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.text)
    exit(1)

models = response.json().get("models", [])
print("Available Gemini/GenAI models:")
for model in models:
    print(f"- {model.get('name')}")
    if 'supportedGenerationMethods' in model:
        print(f"  Supported methods: {model['supportedGenerationMethods']}")
