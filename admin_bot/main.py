# Tidal Force robotics
# 2021, Admin Bot
# MIT License

import os
import sys
import logging

from discord.ext import commands


class AdminBot(object):
    def __init__(self):
        # Create our discord bot
        self.bot = commands.Bot(command_prefix="^")

        # Get the build commit that the code was built with.
        self.version = str(os.environ.get("GIT_COMMIT"))  # Currently running version
        # Find out if we're running in debug mode, or not.
        self.debug = str(os.environ.get("DEBUG")).lower() in ("true", "1", "t")

        # Append our workdir to the path (for importing modules)
        self.workdir = "/app/admin_bot/"
        sys.path.append(self.workdir)

        # Setup logging.
        if self.debug:
            logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
            logging.debug("Running in debug mode.")
        else:
            logging.basicConfig(stream=sys.stderr, level=logging.INFO)
            logging.info("Running in prod mode.")

        # Append some extra information to our discord bot
        self.bot.version = self.version  # Package version with bot

        # Cog Loader!
        for filename in os.listdir(self.workdir + "cogs"):
            logging.info(f"Found file {filename}, loading as extension.")
            if filename.endswith(".py"):
                self.bot.load_extension(f"cogs.{filename[:-3]}")

    def run(self):
        logging.info(f"using version {self.version}")

        # Run the discord bot using our token.
        self.bot.run(str(os.environ.get("BOT_TOKEN")))
