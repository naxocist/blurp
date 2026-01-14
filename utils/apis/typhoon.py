from typing import Optional

from openai import OpenAI

from credentials import TYPHOON_API_KEY

client = OpenAI(api_key=TYPHOON_API_KEY, base_url="https://api.opentyphoon.ai/v1")


def typhoon_inference(system_prompt: str, input_prompt: str) -> Optional[str]:
    model = "typhoon-v2.5-30b-a3b-instruct"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {"role": "user", "content": input_prompt},
            ],
            temperature=0.7,  # Higher for more "rephrasing" variety
        )

        res = response.choices[0].message.content
        if not res:
            return None

        return res

    except Exception as e:
        print(f"Typhoon inference Error: {e}")
        return None
