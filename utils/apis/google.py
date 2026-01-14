from typing import Optional

from google import genai
from google.genai import types

client = genai.Client()


def google_inference(system_prompt: str, input_prompt: str) -> Optional[str]:
    model = "gemini-3-flash-preview"
    try:
        response = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
            contents=input_prompt,
        )

        return response.text

    except Exception as e:
        print(f"Google inference Error: {e}")
        return None
