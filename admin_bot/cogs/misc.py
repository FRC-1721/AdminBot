# Tidal Force robotics
# 2021, Admin Bot
# MIT License


import discord
import logging
import cv2 as cv
import io
import discord.utils

from discord import app_commands
from discord.ext import commands


class MiscCog(commands.Cog, name="Misc"):
    def __init__(self, bot):
        self.bot = bot

        # Variables
        self.bee_movie_line = 0

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

    @app_commands.command(name="snap")
    @app_commands.checks.has_role("Team Member")
    async def snap(self, ctx: discord.Interaction):
        """
        Snaps a photo from the build space!

        Ex: ^snap

        Written by Joe
        """

        # Set capture device
        cap = cv.VideoCapture(0)

        # Set resolution (try to anyway)
        HIGH_VALUE = 10000
        WIDTH = HIGH_VALUE
        HEIGHT = HIGH_VALUE
        fourcc = cv.VideoWriter_fourcc(*"MJPG")
        cap.set(cv.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, HEIGHT)

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


async def setup(bot):
    await bot.add_cog(MiscCog(bot))
