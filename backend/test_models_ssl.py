import os
import httpx
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Bypass SSL verify for the local proxy
http_client = httpx.Client(verify=False)

client = genai.Client(
    api_key=os.environ.get("GOOGLE_API_KEY"),
    http_options={'api_version': 'v1beta'}
)
# Patch the internal httpx client to ignore SSL (very hacky for google-genai, but works for checking)
client._api_client._http_client = httpx.Client(verify=False)

print("Listing models:")
try:
    for model in client.models.list():
        print(model.name)
except Exception as e:
    print(f"Error: {e}")
