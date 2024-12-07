# Tidal Force robotics
# 2021, Admin Bot
# MIT License


import io
import os
import yaml
import random
import discord
import logging
import asyncio
import subprocess
import discord.utils

import cv2 as cv

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

    @app_commands.command(name="aaron")
    async def aaron(self, ctx: discord.Interaction):
        """
        Randomly gives you a picture of aaron
        """

        srcdir = "admin_bot/resources/pictures_of_aaron/"

        await ctx.response.send_message(
            file=discord.File(srcdir + random.choice(os.listdir(srcdir)))
        )

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
