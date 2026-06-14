import asyncio
import logging
from typing import Optional

from google import genai
from google.genai import types

log = logging.getLogger("blurp.services.llm")

MODEL = "gemini-3-flash-preview"

_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


async def google_inference(system_prompt: str, input_prompt: str) -> Optional[str]:
    def _call() -> Optional[str]:
        response = _get_client().models.generate_content(
            model=MODEL,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
            contents=input_prompt,
        )
        return response.text

    try:
        return await asyncio.to_thread(_call)
    except Exception as e:
        log.error("Gemini inference error: %s", e)
        return None
