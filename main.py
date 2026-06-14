from blurp.logging_setup import setup_logging

setup_logging()

from blurp.bot import create_bot  # noqa: E402
from blurp.config import settings  # noqa: E402


def main():
    if not settings.discord_bot_token:
        raise RuntimeError("DISCORD_BOT_TOKEN is required")

    bot = create_bot()
    bot.run(settings.discord_bot_token)


if __name__ == "__main__":
    main()
