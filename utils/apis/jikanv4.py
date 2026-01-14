import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from aiolimiter import AsyncLimiter
from jikanpy import Jikan

import utils.mal_model.models as models

limiter = AsyncLimiter(max_rate=3, time_period=1)  # limit to 3 requests per 1 second
executor = ThreadPoolExecutor(max_workers=5)  # limit number of threads

jikan = Jikan()


async def get_random_anime() -> Optional[models.AnimeFull]:
    """
    Fetches a random anime and returns it as a valid AnimeFull model.
    """
    try:
        async with limiter:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                executor, lambda: jikan.random("anime")
            )

            data = response.get("data")
            if data:
                return models.AnimeFull.model_validate(data)
    except Exception as e:
        print(f"Error fetching random anime: {e}")
    return None


async def get_random_character() -> Optional[models.CharacterFull]:
    """
    Fetches a random character and returns it as a valid CharacterFull model.
    """
    try:
        async with limiter:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                executor, lambda: jikan.random("characters")
            )

            data = response.get("data")
            if data:
                return models.CharacterFull.model_validate(data)
    except Exception as e:
        print(f"Error fetching random character: {e}")
    return None


async def get_anime_characters(mal_id: int) -> Optional[models.AnimeCharacters]:
    """
    Fetches characters for a specific anime.
    Returns the AnimeCharacters container model (access list via .data).
    """
    try:
        async with limiter:
            loop = asyncio.get_running_loop()
            # Extension 'characters' returns a list wrapped in a 'data' dict
            response = await loop.run_in_executor(
                executor, lambda: jikan.anime(mal_id, extension="characters")
            )

            if response:
                return models.AnimeCharacters.model_validate(response)
    except Exception as e:
        print(f"Error fetching anime characters: {e}")
    return None


async def get_anime_by_id(mal_id: int) -> Optional[models.AnimeFull]:
    """
    Fetches a specific anime by ID and returns the AnimeFull model.
    """
    try:
        async with limiter:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(executor, lambda: jikan.anime(mal_id))

            data = response.get("data")
            if data:
                return models.AnimeFull.model_validate(data)
    except Exception as e:
        print(f"Error fetching anime by ID: {e}")
    return None
