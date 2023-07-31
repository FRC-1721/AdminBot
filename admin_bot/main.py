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
        intents = discord.Intents(messages=True, guilds=True, members=True)
        intents.message_content = True

        # Create our discord bot
        self.bot = commands.Bot(command_prefix="^", intents=intents)

        # Remove legacy help command
        self.bot.remove_command("help")

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
        logging.basicConfig(
            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
            level=os.environ.get("LOG_LEVEL", "INFO").upper(),
            handlers=[logging.FileHandler("/tmp/adman.log"), logging.StreamHandler()],
        )

        # Append some extra information to our discord bot
        self.bot.version = self.version  # Package version with bot

    async def on_ready(self):
        # Cog Loader!
        for filename in os.listdir(self.workdir + "cogs"):
            logging.info(f"Found file {filename}, loading as extension.")
            if filename.endswith(".py"):
                try:
                    await self.bot.load_extension(f"cogs.{filename[:-3]}")
                except Exception as e:
                    logging.fatal(f"Error loading {filename} as a cog, error: {e}")

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
        logging.debug(f"Checking rick.. {num}")

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

    async def check_spam(self, ctx: discord.Interaction):
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
            await ctx.response.send_message("❌")
            return True  # Return true, (cancel command)

        return False

    async def reacts(self, ctx):
        """
        Reacts to things!
        """

        reactPairs = [
            ["joe", "wide_joe"],
            ["mat", "Mat"],
            ["mark", "3dprint_mork"],
            ["mike", "weldin_time"],
            ["toast", "Toaster"],
            ["code", "sofware"],
        ]

        userPairs = [
            ["younglad", "capn"],
            ["G!", "saftey_captian"],
            ["Casey", "CAD"],
        ]

        if ctx.channel.id != 967054609233362946:  # Exclusion for counting channel
            for pair in reactPairs:
                if pair[0] in ctx.content.lower() == pair[0]:
                    try:
                        print(f"Trying to pair {pair[0]} with {pair[1]}.")
                        await ctx.add_reaction(get(self.bot.emojis, name=pair[1]))
                    except TypeError:
                        logging.warn(
                            f"Tried to add {pair[1]} emoji to message with {pair[0]} but failed."
                        )

            for pair in userPairs:
                if ctx.author.name == pair[0]:
                    try:
                        print(f"Trying to give {pair[0]} reaction {pair[1]}.")
                        await ctx.add_reaction(get(self.bot.emojis, name=pair[1]))
                    except TypeError:
                        logging.warn(
                            f"Tried to give {pair[1]} emoji for message with {pair[0]} but failed."
                        )

            # Special case
            if ctx.author.name == "myth 2.0":
                await ctx.add_reaction("🤷‍♀️")


if __name__ == "__main__":
    bot = AdminBot()
    bot.run()
