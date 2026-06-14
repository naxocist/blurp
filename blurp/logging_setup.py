import logging


def setup_logging():
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")

    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    file_handler.setFormatter(formatter)
    discord_logger.addHandler(file_handler)

    app_logger = logging.getLogger("blurp")
    app_logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    app_logger.addHandler(stream_handler)
