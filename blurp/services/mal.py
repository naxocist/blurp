import httpx
from aiolimiter import AsyncLimiter

from blurp.config import settings

limiter = AsyncLimiter(max_rate=1, time_period=1)


async def get_user_anime_list(mal_username: str) -> list[dict] | None:
    if not settings.mal_client_id:
        raise ValueError("MAL_CLIENT_ID must be set")

    headers: dict[str, str] = {"X-MAL-CLIENT-ID": settings.mal_client_id}
    url = f"https://api.myanimelist.net/v2/users/{mal_username}/animelist?limit=1000&nsfw=true"

    animes: list[dict] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        while url:
            async with limiter:
                try:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    result = response.json()
                except httpx.HTTPStatusError as e:
                    print(f"HTTP error: {e.response.status_code}")
                    return None
                except Exception as e:
                    print(f"Request failed: {e}")
                    return None

                animes.extend(result.get("data", []))
                url = result.get("paging", {}).get("next")

    return animes
