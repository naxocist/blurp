import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

log = logging.getLogger("blurp.config")

REQUIRED_KEYS = ["DISCORD_BOT_TOKEN", "MAL_CLIENT_SECRET", "MAL_CLIENT_ID"]


@dataclass
class Settings:
    discord_bot_token: str | None
    mal_client_id: str | None
    mal_client_secret: str | None
    is_dev: bool
    guild_ids: list[int] | None


def _load_settings() -> Settings:
    env = os.getenv("ENV", "production").lower()
    is_dev = env == "dev"

    env_file = ".env.development" if is_dev else ".env.production"
    if os.path.exists(env_file):
        load_dotenv(dotenv_path=env_file)
        log.info("Loaded variables from %s", env_file)
    else:
        log.info("No %s found, using system environment variables", env_file)

    for key in REQUIRED_KEYS:
        if not os.getenv(key):
            raise RuntimeError(f"Missing critical variable: {key}")

    guild_ids: list[int] | None = None
    if is_dev:
        guild_ids = []
        raw = os.getenv("NAXOCIST_GUILD_ID")
        if raw:
            try:
                guild_ids.append(int(raw))
            except ValueError:
                log.warning("Invalid guild ID in environment: %s", raw)
        log.info("Dev mode, registered guilds: %s", guild_ids)
    else:
        log.info("Production mode")

    return Settings(
        discord_bot_token=os.getenv("DISCORD_BOT_TOKEN"),
        mal_client_id=os.getenv("MAL_CLIENT_ID"),
        mal_client_secret=os.getenv("MAL_CLIENT_SECRET"),
        is_dev=is_dev,
        guild_ids=guild_ids,
    )


settings = _load_settings()
