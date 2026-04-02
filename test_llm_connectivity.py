
import os
import sys
from pathlib import Path

# Add project root and backend to sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend"))

from dotenv import load_dotenv
load_dotenv()

import ssl
import httpx
import warnings
import asyncio

# Disable SSL verification (mirroring main.py)
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore")

_original_async_init = httpx.AsyncClient.__init__
def _patched_async_init(self, *args, **kwargs):
    kwargs["verify"] = False
    _original_async_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = _patched_async_init

from backend.app.core.llm_factory import get_llm

async def test_groq():
    print("Testing Groq Connectivity...")
    print(f"Model: {os.getenv('GROQ_MODEL')}")
    try:
        llm = get_llm()
        # Simple invoke
        print("Invoking LLM...")
        response = await llm.ainvoke("Say hello")
        print(f"Success! Response: {response.content}")
    except Exception as e:
        print(f"Failed! Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_groq())
