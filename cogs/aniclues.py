import asyncio
from random import randint

import discord
from discord import ApplicationContext, Bot, Color, Embed, Member
from discord.ext import commands

from credentials import guild_ids
from utils.apis.jikanv4 import get_anime_by_id
from utils.apis.MAL import get_user_anime_list
from utils.customs.aniclues.comps import ClueClass
from utils.customs.states import Answer, minigame_objects, players_games
from utils.template.embed import make_timer_embed
from utils.template.response import sendError


class AniClues(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    clues = discord.SlashCommandGroup(
        "clues",
        "Guessing random anime from a MAL profile minigame based on clues",
        guild_ids=guild_ids,
    )

    @clues.command(description="start guessing random anime from given MAL profile!")
    async def init(self, ctx: ApplicationContext, mal_username: str):
        await ctx.defer()
        if not isinstance(ctx.author, Member):
            return

        if ctx.author in players_games:
            await ctx.respond(
                "You are currently in other minigame! Finish that first...",
                ephemeral=True,
            )
            return

        animes = await get_user_anime_list(mal_username)
        if not animes or len(animes) == 0:
            await ctx.followup.send(
                embed=Embed(
                    title="Error",
                    description=f"Could not retrieve anime list for user  \
                            `{mal_username}` or the list is empty. \
                            Please check the username.",
                    color=Color.red(),
                )
            )
            return

        random_idx = randint(0, len(animes) - 1)
        anime_id = animes[random_idx]["node"]["id"]

        anime = await get_anime_by_id(anime_id)
        if not anime:
            await sendError(
                ctx,
                "Failed to choose an anime for u🥲, Try again later or try another MAL username",
            )
            return

        clue_obj = ClueClass(anime)
        await clue_obj.prepare()

        await ctx.respond(
            embed=Embed(
                title="Anime Clues initialized!",
                description=f"You will be guessing a random anime from \
                        [{mal_username}](https://myanimelist.net/profile/{mal_username}) \
                        profile!\n As clues are gradually revealed...",
                color=Color.blurple(),
            )
        )

        minigame_objects.append(clue_obj)
        players_games[ctx.author] = clue_obj

        # Send first clue & timer
        crr_clue_embed = clue_obj.current_embed
        await ctx.send(embed=crr_clue_embed)

        timer = clue_obj.timer
        timer_msg = await ctx.send(
            embed=make_timer_embed("Time until next clue: ", timer)
        )

        while True:
            sleep_task = asyncio.create_task(asyncio.sleep(1))
            answered_task = asyncio.create_task(clue_obj.answered_event.wait())
            done, _ = await asyncio.wait(
                [sleep_task, answered_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            async def next_clue_and_new_timer():
                nonlocal timer, timer_msg
                clue_obj.advance_clue()
                clue_obj.status = Answer.NOT_ANSWERED

                crr_clue_embed = clue_obj.current_embed
                if clue_obj.current_clue_index == 4:
                    if clue_obj.blurred_image_file:
                        await ctx.send(
                            file=clue_obj.blurred_image_file, embed=crr_clue_embed
                        )
                    else:
                        await ctx.send("Image not found...T-T")
                else:
                    await ctx.send(embed=crr_clue_embed)

                await timer_msg.delete()
                timer = clue_obj.timer
                timer_msg = await ctx.send(
                    embed=make_timer_embed(
                        f"{'Time until solution: ' if clue_obj.is_last_clue else 'Time until next clue: '}",
                        timer,
                    )
                )

            if answered_task in done:
                clue_obj.answered_event.clear()

                # correct answer or out of clues, terminate
                if clue_obj.status == Answer.ANSWERED_CORRECT or clue_obj.is_last_clue:
                    await timer_msg.delete()
                    break

                # incorrect answer and clues left, send next clue & new timer
                await next_clue_and_new_timer()
            else:
                timer -= 1
                # TIMEOUT

                if timer == 0:
                    # out of clues
                    if clue_obj.is_last_clue:
                        await timer_msg.delete()
                        break
                    # send next clue & new timer
                    await next_clue_and_new_timer()

            if timer % 5 == 0 or timer <= 5:
                await timer_msg.edit(
                    embed=make_timer_embed(
                        f"{'Time until solution: ' if clue_obj.is_last_clue else 'Time until next clue: '}",
                        timer,
                    ),
                )

        if clue_obj.is_last_clue:
            await ctx.send(
                embed=Embed(
                    title=anime.title,
                    description="This is the answer... Try again next time!",
                    url=anime.url,
                    image=(
                        anime.images.jpg.image_url
                        if anime.images and anime.images.jpg
                        else ""
                    ),
                    color=Color.brand_red(),
                )
            )

        minigame_objects.remove(clue_obj)
        players_games.pop(ctx.author)

    @clues.command(description="submit your guess!")
    async def answer(self, ctx: ApplicationContext, anime_id: int):
        if not isinstance(ctx.author, Member):
            return

        member: Member = ctx.author
        clues_obj = players_games.get(member)

        if not clues_obj:
            await ctx.respond("You are not in any minigame!", ephemeral=True)
            return

        if not isinstance(clues_obj, ClueClass):
            await ctx.respond("You are not in aniclues minigame...", ephemeral=True)
            return

        anime = clues_obj.anime
        if anime_id == anime.mal_id:
            await ctx.respond(
                f"You're right!, used {clues_obj.current_clue_index + 1} clue(s)",
                embed=Embed(
                    title=anime.title,
                    url=anime.url,
                    image=(
                        anime.images.jpg.image_url
                        if anime.images and anime.images.jpg
                        else ""
                    ),
                    color=Color.green(),
                ),
            )
            clues_obj.status = Answer.ANSWERED_CORRECT
        else:
            answered_anime = await get_anime_by_id(anime_id)
            if not answered_anime:
                await ctx.respond("Invaid anime id...", ephemeral=True)
                return

            await ctx.respond(
                f"Nah, [{answered_anime.title}]({answered_anime.url}) is not quite right. Revealing next clue...",
            )
            clues_obj.status = Answer.ANSWERED_WRONG

        clues_obj.answered_event.set()  # trigger answered event


def setup(bot: Bot):
    bot.add_cog(AniClues(bot))
