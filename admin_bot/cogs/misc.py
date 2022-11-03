# Tidal Force robotics
# 2021, Admin Bot
# MIT License


import discord
import logging
import cv2 as cv
import io
import discord.utils

from discord.ext import commands


class MiscCog(commands.Cog, name="Misc"):
    def __init__(self, bot):
        self.bot = bot

        # Variables
        self.bee_movie_line = 0

    @commands.command()
    async def bee(self, ctx, *args):
        """
        Prints a single line from the bee movie script.

        Ex: ^bee

        Written by Joe + Casey, made as a request from https://github.com/FRC-1721/AdminBot/issues/7
        """

        # Random chance to rick-roll
        if await self.bot.rick(ctx):
            return

        if await self.bot.check_spam(ctx):
            return

        with open("admin_bot/resources/bee_movie.md") as f:
            while self.bee_movie_line < 4000:
                line = f.readlines()[self.bee_movie_line].rstrip()
                self.bee_movie_line += 1
                if len(line) != 0:
                    break

        await ctx.send(str(line))

    @commands.command()
    async def snap(self, ctx, *args):
        """
        Snaps a photo from the build space!

        Ex: ^snap

        Written by Joe
        """

        # Set capture device
        cap = cv.VideoCapture(0)

        # Set resolution (3264X2448@15fps)
        # cap.set(cv.CAP_PROP_FRAME_WIDTH, 3264)
        # cap.set(cv.CAP_PROP_FRAME_HEIGHT, 2448)

        if not cap.isOpened():
            await ctx.send(str("Error opening camera.."))
            return

            # Capture a frame
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            await ctx.send(str("Error receiving frame."))
            return

        cv.imwrite("/tmp/snap.png", frame)
        await ctx.send(file=discord.File("/tmp/snap.png"))

    @commands.command()
    async def beeReset(self, ctx):
        """
        Resets the bee command to start back at the begging of the script.

        ex: ^beeReset

        Written by Jack.
        """

        # Random chance to rick-roll
        if await self.bot.rick(ctx):
            return

        if await self.bot.check_spam(ctx):
            return

        if not discord.utils.get(ctx.guild.members, name="darkstar"):
            self.bee_movie_line = 0
            await ctx.send(str("Bee movie script has been reset"))
        else:
            await ctx.message.add_reaction("😂")
            await ctx.send(
                str(
                    "you, darkstar, can no longer use this command. Better luck next time!"
                )
            )


async def setup(bot):
    await bot.add_cog(MiscCog(bot))
