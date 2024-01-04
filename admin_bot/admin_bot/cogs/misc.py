# Tidal Force robotics
# 2021, Admin Bot
# MIT License


import discord
import logging
import cv2 as cv
import io
import os
import random
import discord.utils
import asyncio
import random
import yaml
import subprocess

from PIL import Image, ImageDraw, ImageFilter, UnidentifiedImageError

from discord import app_commands
from discord.ext import commands

from admin_bot.utilities.yamlTools import getSuggestion


class MiscCog(commands.Cog, name="Misc"):
    def __init__(self, bot):
        self.bot = bot

        # Variables
        self.bee_movie_line = 0
        self.robot_channel = self.bot.get_channel(590931089426612284)

    @app_commands.command(name="bee")
    async def bee(self, ctx: discord.Interaction):
        """
        Prints a single line from the bee movie script.

        Ex: ^bee

        Written by Joe + Casey, made as a request from https://github.com/FRC-1721/AdminBot/issues/7
        """

        if await self.bot.check_spam(ctx):
            return

        with open("admin_bot/resources/bee_movie.md") as f:
            while self.bee_movie_line < 4000:
                line = f.readlines()[self.bee_movie_line].rstrip()
                self.bee_movie_line += 1
                if len(line) != 0:
                    break

        await ctx.response.send_message(str(line))

    @app_commands.command(name="myvote")
    async def myvote(self, ctx: discord.Interaction, img: str):
        """
        Automates that silly thing Aaron does.
        """

        # This is literally begging to be used for remote code injection
        subprocess.run(["wget", img, "-O", "/tmp/to_vote.png"])

        try:
            pip = Image.open("/tmp/to_vote.png")
            frame = Image.open("admin_bot/resources/vote.png")

            pip = pip.resize((375, 250))

            frame.paste(pip, (40, 240))
            frame.save("/tmp/myvoteout.png", quality=95)

            await ctx.response.send_message(file=discord.File("/tmp/myvoteout.png"))
        except UnidentifiedImageError:
            logging.error("Could not download image when requested.")
            await ctx.response.send_message("Error opening that image!")

    @app_commands.command(name="aaron")
    async def aaron(self, ctx: discord.Interaction):
        """
        Randomly gives you a picture of aaron
        """

        srcdir = "admin_bot/resources/pictures_of_aaron/"

        await ctx.response.send_message(
            file=discord.File(srcdir + random.choice(os.listdir(srcdir)))
        )

    @app_commands.command(name="whiteboard")
    async def whiteboard(self, ctx: discord.Interaction, img: str):
        """
        Puts a thing on the whiteboard
        """

        await ctx.response.defer()  # We can expect that this command will take a while

        subprocess.run(["wget", img, "-O", "/tmp/to_vote.png"])

        try:
            background = Image.open("admin_bot/resources/look_at_this/background.png")
            pip = Image.open("/tmp/to_vote.png")
            foreground = Image.open("admin_bot/resources/look_at_this/foreground.png")

            pip = pip.resize((1000, 2000))

            background.paste(pip, (1500, 75))
            background.paste(
                foreground,
                (0, 0),
                foreground,  # Transparency layer
            )
            background.save("/tmp/myvoteout.png", quality=95)

            await ctx.followup.send(file=discord.File("/tmp/myvoteout.png"))
        except UnidentifiedImageError:
            logging.error("Could not download image when requested.")
            await ctx.followup.send("Error opening that image!")

    @app_commands.command(name="snap")
    async def snap(self, ctx: discord.Interaction):
        """
        Snaps a photo from the build space!

        Ex: ^snap

        Written by Joe
        """

        # Set capture device
        cap = cv.VideoCapture(0)

        # # Set resolution (3264X2448@15fps)
        # fourcc = cv.VideoWriter_fourcc(*"MJPG")
        # cap.set(cv.CAP_PROP_FRAME_WIDTH, 1600)
        # cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1200)

        if not cap.isOpened():
            await ctx.response.send_message(str("Error opening camera.."))
            return

            # Capture a frame
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            await ctx.response.send_message(str("Error receiving frame."))
            return

        cv.imwrite("/tmp/snap.png", frame)
        await ctx.response.send_message(file=discord.File("/tmp/snap.png"))

    @app_commands.command(name="beereset")
    async def beeReset(self, ctx: discord.Interaction):
        """
        Resets the bee command to start back at the begging of the script.

        ex: ^beeReset

        Written by Jack.
        """

        if await self.bot.check_spam(ctx):
            return
        if ctx.user.name != "darkstar":
            self.bee_movie_line = 0
            await ctx.response.send_message(str("Bee movie script has been reset"))
        else:
            await ctx.message.add_reaction("😂")
            await ctx.response.send_message(
                str(
                    "you, Logan(AKA darkstar), can no longer use this command. Better luck next time!"
                )
            )

    @app_commands.command(name="help")
    async def help(self, ctx: discord.Interaction):
        """Its like a real help, but silly"""

        await ctx.response.send_message(
            random.choice(getSuggestion([role.name for role in ctx.user.roles]))
        )


async def setup(bot):
    await bot.add_cog(MiscCog(bot))
