import logging
import pkgutil

import discord

import blurp.cogs

log = logging.getLogger("blurp.bot")


def _extension_names() -> list[str]:
    package = blurp.cogs
    return [
        info.name
        for info in pkgutil.walk_packages(package.__path__, package.__name__ + ".")
        if not info.ispkg
    ]


def load_extensions(bot: discord.Bot) -> None:
    for name in _extension_names():
        try:
            bot.load_extension(name)
            log.info("Loaded extension %s", name)
        except Exception as e:
            log.exception("Failed to load extension %s: %s", name, e)


def create_bot() -> discord.Bot:
    intents = discord.Intents.default()
    intents.message_content = True

    bot = discord.Bot(
        description="The versatile anime related discord bot", intents=intents
    )
    bot.activity = discord.Activity(type=discord.ActivityType.watching, name="anime")

    load_extensions(bot)
    return bot
