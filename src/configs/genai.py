from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()
import os

genai_client = genai.Client(
    api_key=str(os.environ.get("GEMINI_API_KEY")),
    http_options=types.HttpOptions(api_version="v1beta")
)