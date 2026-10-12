from src.configs.genai import genai_client
from google.genai import types

def try_gemini_inference(prompt: str) -> str:
    response = genai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
        )
    )

    return response.text