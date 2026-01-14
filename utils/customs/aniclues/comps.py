import asyncio
from typing import List, Optional

import discord
from discord import Color, Embed

from utils.customs.states import Answer
from utils.mal_model.models import AnimeFull
from utils.tools import blur_image_from_url, make_synopsis_clue


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
        """Moves to the next clue and updates the timer."""
        if not self.is_last_clue:
            self.current_clue_index += 1
            self.timer = self.REVEAL_DELAYS[self.current_clue_index]

    async def prepare(self):
        """Asynchronously prepares all clues and assets."""
        data = await self._extract_clue_data()
        self.blurred_image_file = data["file"]
        self.clue_embeds = self._build_embeds(data)

    async def _extract_clue_data(self) -> dict:
        """Extracts and formats data from the AnimeFull model into dict."""
        anime = self.anime

        # Blur Image
        image_file = None
        if anime.images and anime.images.jpg:
            img_url = anime.images.jpg.image_url
            if img_url:
                buffer = blur_image_from_url(img_url, 50)
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
        """Create list of Embed objects based on dict data."""
        description = "use `/clues answer <anime_id>` to answer!"

        embeds = [
            # Clue #1: Basic Info
            Embed(
                title="Clue #1: Basic information",
                color=Color.red(),
                description=description,
            )
            .add_field(name="Genres", value=data["genres"])
            .add_field(name="Themes", value=data["themes"])
            .add_field(name="Season/Year", value=f"`{data['season_str']}`"),
            # Clue #2: Stats
            Embed(
                title="Clue #2: Do some stats help?",
                color=Color.red(),
                description=description,
            )
            .add_field(name="Episodes", value=f"`{data['episodes']}` episodes")
            .add_field(name="Score", value=data["score"])
            .add_field(name="Ranked", value=f"`{data['rank']}`"),
            # Clue #3: Production
            Embed(
                title="Clue #3: Who created this?",
                color=Color.orange(),
                description=description,
            )
            .add_field(name="Studios", value=data["studios"])
            .add_field(name="Producers", value=data["producers"]),
            # Clue #4: Synopsis
            Embed(
                title="Clue #4: You should recognize this",
                color=Color.green(),
                description=description,
            ).add_field(name="Summarized synopsis", value=data["synopsis"]),
            # Clue #5: Image
            Embed(
                title="Clue #5: Okay...", color=Color.green(), description=description
            ).set_image(url="attachment://blurred.png"),
        ]

        return embeds


# import asyncio
# from enum import Enum
# from typing import List
#
# import discord
# from discord import Color, Embed
#
# from utils.mal_model.models import AnimeFull
# from utils.template.embed import make_anime_embed
# from utils.tools import blur_image_from_url, make_synopsis_clue
#
#
# class ClueAnswer(Enum):
#     NOT_ANSWERED = 0
#     ANSWERED_WRONG = 1
#     ANSWERED_CORRECT = 2
#
#
# class ClueClass:
#     clues_embed = []
#     clues_reveal_after: List[int] = [60, 60, 60, 60, 30]
#     delay = 20
#
#     def __init__(self, anime: AnimeFull):
#         self.crr_clue_idx: int = 0
#         self.anime = anime
#
#         self.timer = ClueClass.clues_reveal_after[0]
#
#         self.just_answered = ClueAnswer.NOT_ANSWERED
#         self.answered_event = asyncio.Event()
#
#     async def _extract_clues(self):
#         anime = self.anime
#         genres = " ".join(f"`{genre.name}`" for genre in (anime.genres or [])) or "N/A"
#         themes = (
#             " ".join(f"`{theme.name}`" for theme in (anime.themes or [])) or "`N/A`"
#         )
#         studios = (
#             " ".join(f"`{studio.name}`" for studio in (anime.studios or [])) or "N/A"
#         )
#         producers = (
#             " ".join(f"`{producer.name}`" for producer in (anime.producers or []))
#             or "N/A"
#         )
#
#         season = anime.season
#         year = anime.year
#         episodes = anime.episodes or "`N/A`"
#
#         score = f"`{anime.score}`/10" if anime.score is not None else "`N/A`"
#         ranked = f"#{anime.rank}" if anime.rank is not None else "N/A"
#
#         synopsis_clue = await make_synopsis_clue(self.anime)
#         image_url = ""
#         if anime.images and anime.images.jpg:
#             image_url = anime.images.jpg.image_url or ""
#
#             file_buffer = blur_image_from_url(image_url, 50)
#             if file_buffer:
#                 self.file = discord.File(fp=file_buffer, filename="blurred.png")
#
#         return (
#             anime,
#             genres,
#             themes,
#             studios,
#             producers,
#             season,
#             year,
#             episodes,
#             score,
#             ranked,
#             synopsis_clue,
#             file_buffer,
#         )
#
#     async def setup_clues(self):
#         (
#             anime,
#             genres,
#             themes,
#             studios,
#             producers,
#             season,
#             year,
#             episodes,
#             score,
#             ranked,
#             synopsis_clue,
#             file_buffer,
#         ) = await ClueClass._extract_clues(self)
#
#         description = "use `/clues answer <anime_id>` to answer!"
#         ClueClass.clues_embed = [
#             # Clue #1: Genres, The es, Season/Year
#             Embed(
#                 title="Clue #1: Basic information",
#                 color=Color.red(),
#                 description=description,
#             )
#             .add_field(name="Genres", value=genres, inline=True)
#             .add_field(name="Themes", value=themes, inline=True)
#             .add_field(
#                 name="Season/Year",
#                 value=f"`{season.capitalize() + ' ' + str(year) if season and year else 'N/A'}`",
#                 inline=True,
#             ),
#             # Clue #2: Eps, Score, Ranked
#             Embed(
#                 title="Clue #2: Do some stats help?",
#                 color=Color.red(),
#                 description=description,
#             )
#             .add_field(name="Episodes", value=f"`{episodes}` episodes", inline=True)
#             .add_field(name="Score", value=score, inline=True)
#             .add_field(name=f"Ranked: `{ranked}`", value="", inline=True),
#             # Clue #3: Studio, Producers
#             Embed(
#                 title="Clue #3: Who created this!?",
#                 color=Color.orange(),
#                 description=description,
#             )
#             .add_field(name="Studios", value=studios)
#             .add_field(name="Producers", value=producers),
#             # Clue #4: Synopsis
#             Embed(
#                 title="Clue #4: You should recognize this",
#                 color=Color.green(),
#                 description=description,
#             ).add_field(name="Summarized synopsis", value=synopsis_clue),
#             # Clue #5: Image Cover
#             Embed(
#                 title="Clue #5: Okay...",
#                 color=Color.green(),
#                 description=description,
#             ).set_image(url="attachment://blurred.png"),
#         ]
#
#     def get_current_embed(self) -> Embed:
#         return ClueClass.clues_embed[self.crr_clue_idx]
#
#     def next_clue(self):
#         self.crr_clue_idx += 1
#         self.timer = ClueClass.clues_reveal_after[self.crr_clue_idx]
#
#     def is_last_clue(self):
#         return self.crr_clue_idx == len(ClueClass.clues_embed) - 1
