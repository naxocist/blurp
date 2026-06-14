from typing import cast

import discord
from discord import ApplicationContext, Bot, Color, Embed, Interaction, Member
from discord.ext import commands
from dotmap import DotMap

from blurp.config import settings
from blurp.services.jikan import get_anime_by_id
from blurp.games.cycle.game import CycleClass
from blurp.games.cycle.flow import (
    game_phase,
    init_phase,
    pick_phase,
    random_phase,
)
from blurp.games.state import Answer, registry
from blurp.models.models import AnimeFull


class AniCycle(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    cycle = discord.SlashCommandGroup(
        "cycle", "anime cycle game commands", guild_ids=settings.guild_ids
    )

    @cycle.command(description="Initialize an anime cycle game")
    async def init(self, ctx: ApplicationContext):
        await ctx.defer()

        cycle_obj = None
        try:
            cycle_obj = await init_phase(ctx)
            if not isinstance(cycle_obj, CycleClass):
                return

            pick_msg, pick_view = await random_phase(ctx, cycle_obj)
            await pick_phase(ctx, cycle_obj, pick_msg, pick_view)
            await game_phase(ctx, cycle_obj)
        except Exception:
            await ctx.send("An Error occured..., Try again later.")
        finally:
            if cycle_obj is not None:
                cycle_obj.clean()

    @cycle.command(description="Pick an anime for your assigned player")
    async def pick(self, ctx: ApplicationContext, anime_id: int):
        if not isinstance(ctx.author, Member):
            return

        member: Member = ctx.author
        cycle_obj = registry.get(member)
        if cycle_obj is None:
            return

        if not cycle_obj:
            await ctx.respond("You are not in any anime cycle game.", ephemeral=True)
            return

        if cycle_obj.current_phase() != "picking":
            await ctx.respond("The game is not in the picking phase!", ephemeral=True)
            return

        result = await get_anime_by_id(anime_id)
        if not result:
            await ctx.respond("Invalid anime id was provided.", ephemeral=True)
            return

        image_url = ""
        if result.images and result.images.jpg:
            image_url = result.images.jpg.image_url or ""

        title, url, mal_id = (
            result.title,
            result.url,
            result.mal_id,
        )

        target: Member = cycle_obj.targets[member]
        cycle_obj.player_animes[target] = DotMap(
            dict(title=title, url=url, mal_id=mal_id)
        )

        pick_embed = Embed(
            description=f"You picked **[{title}]({url})** for {target.mention}!",
            image=image_url,
            color=Color.nitro_pink(),
        )
        await ctx.respond(embed=pick_embed, ephemeral=True)

        cycle_obj.add_picked(member)

    @cycle.command(description="Submit your answer here!")
    async def answer(self, ctx: ApplicationContext, anime_id: int):
        member = ctx.author
        if not isinstance(member, Member):
            return

        cycle_obj = registry.get(member)

        if not cycle_obj:
            await ctx.respond("You are not in any anime cycle game.", ephemeral=True)
            return

        if not isinstance(cycle_obj, CycleClass):
            await ctx.respond("You are not in anicycle minigame...", ephemeral=True)
            return

        if cycle_obj.current_phase() != "turns":
            await ctx.respond("The game is not in the turns phase!", ephemeral=True)
            return

        if member != cycle_obj.current_player():
            await ctx.respond("It's not your turn yet!", ephemeral=True)
            return

        result = await get_anime_by_id(anime_id)
        if not result:
            await ctx.respond("Invalid anime id was provided.", ephemeral=True)
            return

        image_url = ""
        if result.images and result.images.jpg:
            image_url = result.images.jpg.image_url or ""

        title, url, mal_id = (
            result.title,
            result.url,
            result.mal_id,
        )

        target: AnimeFull = cycle_obj.player_animes[member]

        correct = target.mal_id == mal_id
        guessed = f"{member.mention} guessed [{title}]({url})\n"
        embed = Embed(image=image_url)

        if correct:
            cycle_obj.status = Answer.ANSWERED_CORRECT
            guessed += "**Correct!** 🤓"
            embed.color = Color.brand_green()
            cycle_obj.add_done(member)
            cycle_obj.turn_done[member] = cycle_obj.round
        else:
            cycle_obj.status = Answer.ANSWERED_WRONG
            guessed += "**Not quite right... Try again!** 🥹"
            embed.color = Color.brand_red()

        embed.description = guessed
        answer_msg = await ctx.respond(embed=embed)
        cycle_obj.answered_event.set()

        answer_msg = cast(Interaction, answer_msg)
        msg = await answer_msg.original_response()
        await msg.delete(delay=5)


def setup(bot: Bot):
    bot.add_cog(AniCycle(bot))
