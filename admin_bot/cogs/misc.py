# Tidal Force robotics
# 2021, Admin Bot
# MIT License


import discord
import logging

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
        if self.bot.rick():
            return

        with open("admin_bot/resources/bee_movie.md") as f:
            while self.bee_movie_line < 4000:
                line = f.readlines()[self.bee_movie_line].rstrip()
                self.bee_movie_line += 1
                if len(line) != 0:
                    break

        await ctx.send(str(line))


def setup(bot):
    bot.add_cog(MiscCog(bot))
