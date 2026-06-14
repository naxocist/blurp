import asyncio
from math import floor
from typing import cast

import discord
from discord import ApplicationContext, Bot, Color, Embed, Member, Option
from discord.ext import commands

from blurp.config import settings
from blurp.games.state import Answer, registry
from blurp.games.whatnum.game import BinarySearch


class WhatNum(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    binary_search = discord.SlashCommandGroup(
        "whatnum",
        "Try to guess a random number",
        guild_ids=settings.guild_ids,
    )

    @binary_search.command(
        description="Try to guess a random number with least possible guess"
    )
    async def init(
        self,
        ctx: ApplicationContext,
        low=Option(int, "The lower bound (default = 1)", default=1),
        high=Option(int, "The upper bound (default = 100)", default=100),
    ):
        member = ctx.author
        if not isinstance(member, Member):
            return

        low = cast(int, low)
        high = cast(int, high)

        if member in registry:
            await ctx.respond(
                "You are in other minigames! Finish that first...", ephemeral=True
            )
            return

        if low >= high:
            await ctx.respond("low must less than high!", ephemeral=True)
            return

        bs_obj = BinarySearch(low, high)
        registry.bind(member, bs_obj)

        await ctx.respond(
            embed=Embed(
                title=f"Guess a number from {bs_obj.low} to {bs_obj.high}",
                description=f"use `/whatnum guess <number>` to apply guess.\nI'll tell you whether your guess is less or greater than target number\n**You have {bs_obj.expected_guess_cnt} tries**",
                color=Color.green(),
            )
        )

        timer: int = floor(bs_obj.expected_guess_cnt ** (2.75))
        await ctx.send(f"You have {timer} seconds. Good luck!")

        while timer > 0:
            if bs_obj.status != Answer.NOT_ANSWERED:
                break

            await asyncio.sleep(1)
            timer -= 1

        if timer == 0 or bs_obj.status == Answer.ANSWERED_WRONG:
            await ctx.respond(embed=BinarySearch.fail_embed(str(bs_obj.target)))

        registry.remove(bs_obj)

    @binary_search.command(description="Guess that random number!")
    async def guess(self, ctx: ApplicationContext, guess: int):
        member = ctx.author
        if not isinstance(member, Member):
            return
        bs_obj = registry.get(member)

        if not bs_obj:
            await ctx.respond("You are not in any minigame!", ephemeral=True)
            return

        if not isinstance(bs_obj, BinarySearch):
            await ctx.respond(
                "You are not in a guess number minigame...", ephemeral=True
            )

        target = bs_obj.target
        bs_obj.guess_cnt += 1
        guess_left = bs_obj.expected_guess_cnt - bs_obj.guess_cnt

        msg = f"That's correct🤓 You've guessed **{bs_obj.guess_cnt}** time(s) to get to {target}"

        if guess == target:
            await ctx.respond(
                embed=Embed(title="Congrats!", description=msg, color=Color.green())
            )
            bs_obj.terminate(True)
            return

        if guess > target:
            msg = f"{guess} is too large... {guess_left} {'tries' if guess_left > 1 else 'try'} left"
        elif guess < target:
            msg = f"{guess} is too small... {guess_left} {'tries' if guess_left > 1 else 'try'} left"

        if guess_left == 0:
            bs_obj.terminate(False)
            return

        await ctx.respond(msg)

    @binary_search.command(description="For real!? plz don't")
    async def giveup(self, ctx: ApplicationContext):
        member = ctx.author
        if not isinstance(member, Member):
            return
        bs_obj = registry.get(member)

        if not bs_obj:
            await ctx.respond("You can't give up on nothing...", ephemeral=True)
            return

        if not isinstance(bs_obj, BinarySearch):
            await ctx.respond(
                "You are not in a guess number minigame...", ephemeral=True
            )

        await ctx.respond("🤓☝️")
        bs_obj.terminate(False)


def setup(bot):
    bot.add_cog(WhatNum(bot))
