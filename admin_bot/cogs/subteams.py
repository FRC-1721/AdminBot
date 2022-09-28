# Tidal Force robotics
# 2021, Admin Bot
# MIT License


from types import NoneType
import discord
import logging

from discord.ext import commands


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
        # try:
        request_role = args[0].lower()
        role = self.self_assignable_roles[request_role]

        user = ctx.message.author

        logging.info(f"Attempting to add user to {role}")

        targetRole = discord.utils.get(ctx.message.guild.roles, name=role)

        await user.add_role(targetRole)
        await ctx.send(f"You've been added to the following roles: {role}")
        # except KeyError:
        #     await ctx.send(
        #         "Sorry, i could not interpert that, try something like ^join CAD"
        #     )

    @commands.command()
    @commands.has_role("Team Member")
    async def leave(self, ctx, *args, member: discord.Member = None):
        """
        Removes a user from a subteam (or subteams),

        ex: ^leave Software

        Written by Joe.
        """

        # Adds a user to a group
        roles = args[1:]
        role_objects = []
        user = ctx.message.author
        if all(item in self.self_assignable_roles for item in roles):
            for role in roles:
                role_objects.append(
                    discord.utils.get(ctx.message.guild.roles, name=role)
                )

            await user.remove_roles(*role_objects)
            await ctx.send(f"You've been removed from the following roles: {roles}")
        else:
            await ctx.send(
                f"Invalid role name or unassignable role (make sure you spelt it correctly, and used qoutes, ie: `Kode Team` or `Chairmans`) Role was: {roles}"
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
