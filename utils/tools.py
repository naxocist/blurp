import asyncio
from io import BytesIO
from typing import Callable

import cv2
import numpy as np
import requests
from discord import ApplicationContext
from PIL import Image

from utils.apis.jikanv4 import get_anime_characters
from utils.apis.typhoon import inference
from utils.mal_model.models import AnimeFull
from utils.template.embed import make_timer_embed


async def make_synopsis_clue(anime: AnimeFull) -> str:
    names = ""
    if anime.mal_id:
        try:
            response = await get_anime_characters(anime.mal_id)
            data = getattr(response, "data", [])
            names_list = [
                ch.character.name for ch in data if getattr(ch.character, "name", None)
            ]
            names = ", ".join(names_list)
        except Exception:
            pass  # Keep names_list empty and proceed

    if not anime.synopsis:
        if names == "":
            return "No information available..."
        return "No synopsis available, here's the name list: " + names

    input_prompt = f"""
    REWRITE RULE: Summarize the following anime synopsis.
    STRICT CONSTRAINT: You MUST NOT mention any character names, especially: {names}.
    STRICT CONSTRAINT: Do not mention the anime title.
    GOAL: Focus on the plot, themes, and setting only.

    SYNOPSIS TO REWRITE: {anime.synopsis}
    """

    system_prompt = "You are an anime expert that provides spoiler-free, name-free engaging plot summaries."
    clue = inference(system_prompt, input_prompt)
    return clue or f"A story about: {anime.synopsis[:100]}..."


async def count_down_timer(
    ctx: ApplicationContext,
    timeout: int,
    *,
    title_prefix: str = "Time left:",
    interval: int = 5,
    check_done: Callable | None = None,
):
    if timeout <= 0:
        raise Exception("timeout must be positive value!")

    timer_msg = await ctx.send(embed=make_timer_embed(title_prefix, timeout))
    while timeout > 0:
        await asyncio.sleep(1)  # ping every 1s
        timeout -= 1

        if timeout == 0:
            await timer_msg.delete()
            return

        elif timeout % interval == 0 or timeout <= 5:
            await timer_msg.edit(embed=make_timer_embed(title_prefix, timeout))

        if check_done and check_done():
            if timeout > 0:
                await timer_msg.delete()
            return


def blur_image_from_url(url: str, blur_strength: int = 25) -> BytesIO:
    """
    Downloads an image from a URL, applies Gaussian blur, and returns it as a BytesIO buffer.

    Args:
        url (str): Image URL.
        blur_strength (int): Strength of the Gaussian blur. Must be positive odd integer.

    Returns:
        BytesIO: Blurred image in PNG format.
    """
    # Download and open the image
    response = requests.get(url)
    response.raise_for_status()  # Raise error if download fails
    image = Image.open(BytesIO(response.content)).convert("RGB")

    # Convert to OpenCV format
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Ensure blur kernel is odd
    ksize = max(1, blur_strength | 1)

    # Apply Gaussian blur
    blurred_cv = cv2.GaussianBlur(img_cv, (ksize, ksize), 0)

    # Convert back to PIL Image
    result_image = Image.fromarray(cv2.cvtColor(blurred_cv, cv2.COLOR_BGR2RGB))

    # Save to BytesIO buffer
    buffer = BytesIO()
    result_image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
