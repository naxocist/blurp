from discord import Color, Embed

from blurp.models.models import AnimeFull


def make_anime_embed(anime: AnimeFull) -> Embed:
    title = anime.title or "N/A"
    url = anime.url or ""

    image_url = ""
    if anime.images and anime.images.jpg:
        image_url = anime.images.jpg.image_url or ""

    if anime.genres:
        genres = " ".join(f"`{g.name}`" for g in anime.genres if g.name)
    else:
        genres = "`N/A`"

    if anime.season and anime.year:
        season_str = f"{anime.season.capitalize()} {anime.year}"
    else:
        season_str = "N/A"

    episodes = anime.episodes if anime.episodes is not None else "N/A"
    score = f"`{anime.score}`/10" if anime.score is not None else "`N/A`/10"
    ranked = f"#{anime.rank}" if anime.rank is not None else "N/A"

    embed = Embed(title=title, url=url, color=Color.random())

    if image_url:
        embed.set_image(url=image_url)

    embed.add_field(name="Genres", value=genres, inline=False)
    embed.add_field(name="Season", value=f"`{season_str}`", inline=True)
    embed.add_field(name="Length", value=f"`{episodes}` episodes", inline=True)
    embed.add_field(name="Score", value=score, inline=True)
    embed.add_field(name="Ranked", value=ranked, inline=False)

    return embed


def make_timer_embed(title_prefix, timeout) -> Embed:
    return Embed(title=f"{title_prefix} {timeout} seconds", color=Color.dark_magenta())
