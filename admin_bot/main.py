# Tidal Force robotics
# 2021, Admin Bot
# MIT License

import os
import sys
import logging
import random
import discord

from discord.ext import commands
from discord.utils import get


class AdminBot(object):
    def __init__(self):
        # Intents (new iirc)
        intents = discord.Intents(messages=True, guilds=True)
        intents.message_content = True

        # Create our discord bot
        self.bot = commands.Bot(command_prefix="^", intents=intents)

        # Register
        self.bot.on_ready = self.on_ready
        self.bot.on_message = self.on_message

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

    async def on_ready(self):
        # Cog Loader!
        for filename in os.listdir(self.workdir + "cogs"):
            logging.info(f"Found file {filename}, loading as extension.")
            if filename.endswith(".py"):
                await self.bot.load_extension(f"cogs.{filename[:-3]}")

    async def on_message(self, ctx):
        # hehe, sneaky every time
        await self.bot.rick(ctx)
        await self.bot.reacts(ctx)

        await self.bot.process_commands(ctx)

    def run(self):
        logging.info(f"using version {self.version}")

        # Create custom bound entries
        self.bot.rick = self.rick
        self.bot.reacts = self.reacts
        self.bot.check_spam = self.check_spam

        # Run the discord bot using our token.
        self.bot.run(str(os.environ.get("BOT_TOKEN")))

    async def rick(self, ctx):
        """
        Sometimes, randomly rickrolls you.
        """

        num = random.randint(1, 1000)
        logging.info(f"Checking rick.. {num}")

        if num == 1:
            num = random.randint(1, 10)

            if num == 1:
                await ctx.channel.send(
                    str("https://www.youtube.com/watch?v=hYs05S1WBlY")
                )
            else:
                await ctx.channel.send(
                    str("https://www.youtube.com/watch?v=o-YBDTqX_ZU")
                )

            return True
        return False

    async def check_spam(self, ctx):
        """
        Prevents you from spamming some commands in channels where its not allowed
        """

        spam_channels = [
            590931089426612284,
            853061635904503838,
            941894218123710475,
            590349708992708627,
            957837307577241601,
        ]

        if ctx.channel.id not in spam_channels:  # Check if this channel is ok for spam
            await ctx.message.add_reaction("❌")
            return True  # Return true, (cancel command)

        return False

    async def reacts(self, ctx):
        """
        Reacts to things!
        """
        if "joe" in ctx.content.lower():
            await ctx.add_reaction(get(self.bot.emojis, name="wide_joe"))
        if "mat" in ctx.content.lower():
            await ctx.add_reaction(get(self.bot.emojis, name="mat"))
        if "mark" in ctx.content.lower():
            await ctx.add_reaction(get(self.bot.emojis, name="3dprint_mork"))
        if ctx.author.name == "myth 2.0":
            await ctx.add_reaction("🤷‍♀️")
