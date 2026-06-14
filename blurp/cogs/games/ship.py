from discord import ApplicationContext, Bot, SlashCommandGroup
from discord.ext import commands

from blurp.config import settings


class Ship(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    ship = SlashCommandGroup("ship", "shipping minigame", guild_ids=settings.guild_ids)

    @ship.command(guild_ids=settings.guild_ids, description="Just ship 2 anime characters")
    async def init(self, ctx: ApplicationContext):
        await ctx.defer()

        await ctx.respond("end function")


def setup(bot: Bot):
    bot.add_cog(Ship(bot))
