from google import genai
from dotenv import load_dotenv
load_dotenv()
import os

genai_client = genai.Client(api_key=str(os.environ.get("GEMINI_API_KEY")))

# genai_prompt = genai.TextPrompt