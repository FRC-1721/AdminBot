# Tidal Force robotics
# 2021, Admin Bot
# MIT License


from types import NoneType
import discord
import logging

from discord import app_commands
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

    async def rolesAutocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        roles = list(self.self_assignable_roles.values())
        return [
            app_commands.Choice(name=role, value=role)
            for role in roles
            if current.lower() in role.lower()
        ]

    @app_commands.command(name="join")
    @app_commands.checks.has_role("Team Member")
    @app_commands.describe(
        team="Name of the subteam you want to join.",
    )
    @app_commands.autocomplete(team=rolesAutocomplete)
    async def join(self, ctx: discord.Interaction, team: str):
        """
        Adds a user to a subteam.
        """

        # Fuzzy match
        try:
            request_role = team.lower()
            role = self.self_assignable_roles[request_role]

            user = ctx.user

            logging.info(f"Attempting to add user to {role}")

            await user.add_roles(*[get(ctx.guild.roles, name=role)])
            await ctx.response.send_message(
                f"You've been added to the following roles: {role}"
            )
        except (KeyError, AttributeError):
            await ctx.response.send_message(
                "Sorry, i could not interpret that, try something like /join CAD"
            )
        except IndexError:
            await ctx.response.send_message(
                "Please input a subteam, use /listroles to see possible selections"
            )

    @app_commands.command(name="leave")
    @app_commands.checks.has_role("Team Member")
    @app_commands.describe(
        team="Name of the subteam you want to leave.",
    )
    @app_commands.autocomplete(team=rolesAutocomplete)
    async def leave(self, ctx: discord.Interaction, team: str):
        """
        Removes a user from a subteam.
        """

        # Fuzzy match
        try:
            request_role = team.lower()
            role = self.self_assignable_roles[request_role]

            user = ctx.user

            logging.info(f"Attempting to remove user from {role}")

            await user.remove_roles(*[get(ctx.guild.roles, name=role)])
            await ctx.response.send_message(
                f"You've been removed from the following roles: {role}"
            )
        except (KeyError, AttributeError):
            await ctx.response.send_message(
                "Sorry, i could not interpret that, try something like /leave CAD"
            )
        except IndexError:
            await ctx.response.send_message(
                "Please input a subteam, use /listroles to see possible selections"
            )

    @app_commands.command(name="listroles")
    @app_commands.checks.has_role("Team Member")
    async def listroles(
        self,
        ctx: discord.Interaction,
    ):
        """
        Lists the possible roles.
        """

        rolestr = ""
        for role in self.self_assignable_roles:
            rolestr += f"`{role}`, "
        await ctx.response.send_message(f"The possible roles are: {rolestr}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.response.send_message(f"Error! {error}")
        raise error


async def setup(bot):
    await bot.add_cog(SubteamCog(bot))
