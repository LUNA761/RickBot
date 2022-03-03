"""
Copyright (c) 2022, Zach Lagden
All rights reserved.
"""

import logging

from core import RickBot

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)
discordLogger = logging.getLogger("discord")
discordLogger.setLevel(logging.WARNING)


if __name__ == "__main__":
    RickBot().run()
