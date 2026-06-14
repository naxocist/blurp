import asyncio
from typing import List, Optional

import discord
from discord import Color, Embed

from blurp.games.state import Answer
from blurp.models.models import AnimeFull
from blurp.media import blur_image_from_url
from blurp.games.clues.synopsis import make_synopsis_clue


class ClueClass:
    REVEAL_DELAYS = [60, 60, 60, 60, 30]

    def __init__(self, anime: AnimeFull):
        self.anime = anime
        self.current_clue_index: int = 0
        self.clue_embeds: List[Embed] = []
        self.blurred_image_file: Optional[discord.File] = None

        self.timer = self.REVEAL_DELAYS[0]
        self.status = Answer.NOT_ANSWERED
        self.answered_event = asyncio.Event()

    @property
    def current_embed(self) -> Embed:
        return self.clue_embeds[self.current_clue_index]

    @property
    def is_last_clue(self) -> bool:
        return self.current_clue_index >= len(self.clue_embeds) - 1

    def advance_clue(self):
        if not self.is_last_clue:
            self.current_clue_index += 1
            self.timer = self.REVEAL_DELAYS[self.current_clue_index]

    async def prepare(self):
        data = await self._extract_clue_data()
        self.blurred_image_file = data["file"]
        self.clue_embeds = self._build_embeds(data)

    async def _extract_clue_data(self) -> dict:
        anime = self.anime

        image_file = None
        if anime.images and anime.images.jpg:
            img_url = anime.images.jpg.image_url
            if img_url:
                buffer = await blur_image_from_url(img_url, 50)
                if buffer:
                    image_file = discord.File(fp=buffer, filename="blurred.png")

        def join_list(items, default="N/A"):
            if not items:
                return default
            return " ".join(f"`{x.name}`" for x in items)

        synopsis = await make_synopsis_clue(anime)
        synopsis = synopsis[:1024]

        return {
            "genres": join_list(anime.genres),
            "themes": join_list(anime.themes, "`N/A`"),
            "studios": join_list(anime.studios),
            "producers": join_list(anime.producers),
            "season_str": (
                f"{anime.season.capitalize()} {anime.year}"
                if anime.season and anime.year
                else "N/A"
            ),
            "episodes": str(anime.episodes) if anime.episodes else "N/A",
            "score": f"`{anime.score}`/10" if anime.score is not None else "`N/A`",
            "rank": f"#{anime.rank}" if anime.rank is not None else "N/A",
            "synopsis": synopsis,
            "file": image_file,
        }

    def _build_embeds(self, data: dict) -> List[Embed]:
        description = "use `/clues answer <anime_id>` to answer!"

        return [
            Embed(
                title="Clue #1: Basic information",
                color=Color.red(),
                description=description,
            )
            .add_field(name="Genres", value=data["genres"])
            .add_field(name="Themes", value=data["themes"])
            .add_field(name="Season/Year", value=f"`{data['season_str']}`"),
            Embed(
                title="Clue #2: Do some stats help?",
                color=Color.red(),
                description=description,
            )
            .add_field(name="Episodes", value=f"`{data['episodes']}` episodes")
            .add_field(name="Score", value=data["score"])
            .add_field(name="Ranked", value=f"`{data['rank']}`"),
            Embed(
                title="Clue #3: Who created this?",
                color=Color.orange(),
                description=description,
            )
            .add_field(name="Studios", value=data["studios"])
            .add_field(name="Producers", value=data["producers"]),
            Embed(
                title="Clue #4: You should recognize this",
                color=Color.green(),
                description=description,
            ).add_field(name="Summarized synopsis", value=data["synopsis"]),
            Embed(
                title="Clue #5: Okay...", color=Color.green(), description=description
            ).set_image(url="attachment://blurred.png"),
        ]
