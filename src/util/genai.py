from src.configs.genai import genai_client
from google.genai import types

def try_gemini_inference(prompt: str) -> str:

    # response = genai_client.generate_text(
    #     model="gemini-1.5-pro",
    #     # prompt=genai_prompt.from_text(prompt),
    #     prompt=prompt,
    #     max_output_tokens=1024,
    #     temperature=0.7,
    # )

    response = genai_client.models.generate_content(
        model="gemini-2.5-flash",
        # model="gemini-1.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
        )
    )

    return response.text