# Tidal Force robotics
# 2021, Admin Bot
# MIT License


import discord
import logging

from discord.ext import commands


class ToolCog(commands.Cog, name="Tools"):
    def __init__(self, bot):
        self.bot = bot

        # Random chance to rick-roll
        if self.bot.rick():
            return

    @commands.Cog.listener()
    async def on_ready(self):
        status_channel = self.bot.get_channel(590312300695650305)

        await self.bot.get_guild(590309936538451972).me.edit(nick="Adman")

        await status_channel.send(
            f"Admin Bot version `{self.bot.version}` just restarted."
        )

    @commands.command()
    async def version(self, ctx, *, member: discord.Member = None):
        """
        Prints the revision/version.

        Ex: ^version

        Written by Joe.
        """

        await ctx.send(f"I am running version `{self.bot.version}`.")

    @commands.command()
    async def manual(self, ctx, *, member: discord.Member = None):
        """
        Returns the latest infrastructure manual

        Ex: ^manual

        Written by Joe.
        """

        await ctx.send(
            f"Find the build space manual here: https://github.com/FRC-1721/infrastructure/releases/latest/download/FRC1721_Infrastructure_Manual.pdf"
        )

    @commands.command()
    async def feature(self, ctx, *args):
        """
        Allows users to request a feature

        Ex: ^feature Give the bot a self destruct command!

        Written by Joe.
        """

        title = "+".join(args)

        await ctx.send(
            f"https://github.com/FRC-1721/AdminBot/issues/new?labels=feature&title={title}&body=Describe+your+feature+here+please!"
        )

    async def kill(self, ctx):
        await ctx.send(str("shutting off"))
        await ctx.bot.logout()


def setup(bot):
    bot.add_cog(ToolCog(bot))
