from pprint import pprint
from dotmap import DotMap

from discord import ApplicationContext, Bot, SlashCommandGroup
from discord.ext import commands

from credentials import guild_ids
from utils.apis.jikanv4 import get_random_character


class Ship(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    ship = SlashCommandGroup("ship", "shipping minigame", guild_ids=guild_ids)

    @ship.command(guild_ids=guild_ids, description="Get a random anime")
    async def init(self, ctx: ApplicationContext):
        await ctx.defer()

        c1 = await get_random_character()
        c1 = DotMap(c1)
        c1_url = c1.url
        c1_image = c1.images.jpg.image_url
        c1_name = c1.name
        c1_nickname = c1.nickname
        c1_about = c1.about

        c2 = await get_random_character()
        c2 = DotMap(c2)
        c2_url = c2.url
        c2_image = c2.images.jpg.image_url
        c2_nickname = c2.nickname
        c2_about = c2.about

        
        # pprint(character)
        await ctx.respond("Hello World")
        # anime = await get_random_anime()
        # embed = make_anime_embed(anime)
        # response = await ctx.respond(embed=embed)
        # response = cast(Message, response)
        # await discord.Message.add_reaction(response, "📬")


def setup(bot: Bot):
    bot.add_cog(Ship(bot))
