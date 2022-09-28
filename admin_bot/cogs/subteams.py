# Tidal Force robotics
# 2021, Admin Bot
# MIT License


from types import NoneType
import discord
import logging

from discord.ext import commands
from discord.utils import get


class SubteamCog(commands.Cog, name="Subteams"):
    def __init__(self, bot):
        self.bot = bot

        # These should be defined maybe in a yaml somewhere else
        self.self_assignable_roles = {
            "student": "Student",
            "chairmans": "Chairmans",
            "software": "Software Team",
            "mechanical": "Mechanical Team",
            "cad": "CAD Team",
            "electrical": "Electrical Team",
            "outreach": "Outreach",
            "business": "Business Team",
            "scouting": "Scouting",
            "media": "Media",
        }

    @commands.command()
    @commands.has_role("Team Member")
    async def join(self, ctx, *args, member: discord.Member = None):
        """
        Adds a user to a subteam (or subteams),

        ex: ^join Chairmans

        Written by Joe.
        """

        # Fuzzy match
        try:
            request_role = args[0].lower()
            role = self.self_assignable_roles[request_role]

            user = ctx.message.author

            logging.info(f"Attempting to add user to {role}")

            await user.add_roles(*[get(ctx.message.guild.roles, name=role)])
            await ctx.send(f"You've been added to the following roles: {role}")
        except KeyError:
            await ctx.send(
                "Sorry, i could not interpret that, try something like ^join CAD"
            )
        except IndexError:
            await ctx.send(
                "Please input a subteam, use ^listroles to see possible selections"
            )

    @commands.command()
    @commands.has_role("Team Member")
    async def leave(self, ctx, *args, member: discord.Member = None):
        """
        Removes a user from a subteam (or subteams),

        ex: ^leave Software

        Written by Joe.
        """

        # Fuzzy match
        try:
            request_role = args[0].lower()
            role = self.self_assignable_roles[request_role]

            user = ctx.message.author

            logging.info(f"Attempting to remove user from {role}")

            await user.remove_roles(*[get(ctx.message.guild.roles, name=role)])
            await ctx.send(f"You've been removed from the following roles: {role}")
        except KeyError:
            await ctx.send(
                "Sorry, i could not interpret that, try something like ^leave CAD"
            )
        except IndexError:
            await ctx.send(
                "Please input a subteam, use ^listroles to see possible selections"
            )

    @commands.command()
    @commands.has_role("Team Member")
    async def listroles(self, ctx, *args, member: discord.Member = None):
        """
        Lists the possible roles.

        ex: ^listroles

        Written by Joe.
        """

        # Random chance to rick-roll
        if await self.bot.rick(ctx):
            return

        rolestr = ""
        for role in self.self_assignable_roles:
            rolestr += f"`{role}`, "
        await ctx.send(f"The possible roles are: {rolestr}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send(f"Error! {error}")
        raise error


async def setup(bot):
    await bot.add_cog(SubteamCog(bot))
