from blurp.models.models import AnimeFull
from blurp.services.jikan import get_anime_characters
from blurp.services.llm import google_inference


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
            pass

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
    clue = await google_inference(system_prompt, input_prompt)
    return clue or f"A story about: {anime.synopsis[:100]}..."
