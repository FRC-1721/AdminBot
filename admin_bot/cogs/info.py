# Tidal Force robotics
# 2021, Admin Bot
# MIT License


import discord
import logging

from discord.ext import commands


class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        status_channel = self.bot.get_channel(590312300695650305)

        await self.bot.get_guild(590309936538451972).me.edit(nick="Adman")

        await status_channel.send(
            f"Admin Bot version {self.bot.version} just restarted."
        )

    @commands.command()
    async def version(self, ctx, *, member: discord.Member = None):
        """
        Prints the revision/version.

        Ex: ^version

        Written by Joe.
        """

        await ctx.send(f"I am running version {self.bot.version}.")


def setup(bot):
    bot.add_cog(InfoCog(bot))
