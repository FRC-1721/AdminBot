# Tidal Force robotics
# 2021, Admin Bot
# MIT License


from types import NoneType
import discord
import logging

from discord.ext import commands


class SubteamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role("Team Member")
    async def subteam(self, ctx, *args, member: discord.Member = None):
        # These should be defined maybe in a yaml somewhere else
        self_assignable_roles = [
            "Chairmans",
            "Kode Team",
            "Mechanical Team",
            "CAD Team",
            "Electrical Team",
            "Outreach",
            "Business Team",
            "Scouting",
            "Media",
            "Student",
        ]

        # Adds a user to a group
        roles = args[1:]
        role_objects = []
        user = ctx.message.author

        if args[0].lower() == "add":
            logging.info(f"Attempting to add user to {roles}")

            if all(item in self_assignable_roles for item in roles):
                for role in roles:
                    role_objects.append(
                        discord.utils.get(ctx.message.guild.roles, name=role)
                    )

                await user.add_roles(*role_objects)
                await ctx.send(f"You've been added to the following roles: {roles}")
            else:
                await ctx.send(
                    f"Invalid role name or unassignable role (make sure you spelt it correctly, and used qoutes, ie: `Kode Team` or `Chairmans`) Role was: {roles}"
                )

        elif args[0].lower() == "remove":
            if all(item in self_assignable_roles for item in roles):
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

        elif args[0].lower() == "list":
            rolestr = ""
            for role in self_assignable_roles:
                rolestr += f"`{role}`, "
            await ctx.send(f"The possible roles are: {rolestr}")

        else:
            logging.debug(roles)
            await ctx.send(f"Unknown argument {args[0]}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send(f"Error! {error}")

        raise error


def setup(bot):
    bot.add_cog(SubteamCog(bot))
