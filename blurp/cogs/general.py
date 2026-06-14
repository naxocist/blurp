from typing import cast

import discord
from discord import (
    ApplicationContext,
    Bot,
    Color,
    Embed,
    Member,
    Option,
    WebhookMessage,
)
from discord.ext import commands
from nekosbest import Result

from blurp.config import settings
from blurp.services.jikan import get_random_anime
from blurp.services.nekos import get_img, get_phrase, other_actions, self_actions
from blurp.ui.embeds import make_anime_embed


class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @commands.slash_command(guild_ids=settings.guild_ids, description="Get a random anime")
    async def anime(self, ctx: ApplicationContext):
        await ctx.defer()

        anime = await get_random_anime()
        if not anime:
            await ctx.send("Failed to get an anime somehow😭")
            return

        res = await ctx.respond(embed=make_anime_embed(anime))
        if not isinstance(res, WebhookMessage):
            await ctx.send("Internal Error... Try again later.")
            return

        await res.add_reaction("📬")

    @commands.slash_command(guild_ids=settings.guild_ids, description="Express your emotions")
    async def expression(
        self,
        ctx: ApplicationContext,
        action=Option(
            str, "What expression do you want to show?", choices=self_actions
        ),
    ):
        await ctx.defer()

        action = cast(str, action)
        image = cast(Result, await get_img(action))
        phrase = get_phrase(action, ctx.author.mention)
        embed = Embed(image=image.url, color=Color.random())

        await ctx.respond(phrase, embed=embed)

    @commands.slash_command(
        guild_ids=settings.guild_ids, description="Perform an action to another user"
    )
    async def action(
        self,
        ctx: ApplicationContext,
        member: Member,
        action=Option(
            str, "What action do you want to perform?", choices=other_actions
        ),
    ):
        await ctx.defer()
        action = cast(str, action)
        image = cast(Result, await get_img(action))
        phrase = get_phrase(action, ctx.author.mention, member.mention)
        embed = Embed(image=image.url, color=Color.random())

        await ctx.respond(phrase, embed=embed)

    @commands.slash_command(
        guild_ids=settings.guild_ids, description="Get a random anime illustration"
    )
    async def art(
        self,
        ctx: ApplicationContext,
        choice=discord.Option(
            str,
            "Choose your type",
            choices=["husbando", "kitsune", "neko", "waifu"],
        ),
    ):
        await ctx.defer()

        choice = cast(str, choice)
        result = cast(Result, await get_img(choice))

        image = result.url
        artist = result.artist_name or "Unknown"
        artist_href = result.artist_href or "N/A"
        source_url = result.source_url or "N/A"

        embed = Embed(
            title=f"Here is your {choice}!",
            description=f"Artist: **[{artist}]({artist_href})**\nVisit **[source]({
                source_url
            })!**",
            image=image,
            color=Color.random(),
        )

        await ctx.respond(embed=embed)


def setup(bot: Bot):
    bot.add_cog(Anime(bot))
