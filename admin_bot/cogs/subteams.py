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
        self.self_assignable_roles = [
            "Student",
            "Software Team",
            "Mechanical Team",
            "CAD Team",
            "Electrical Team",
            "Outreach",
            "Business Team",
            "Scouting",
            "Media",
            "Gaming Notifications",
        ]

    async def rolesAutocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        roles = self.self_assignable_roles
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
            user = ctx.user

            logging.info(f"Attempting to add user to {team}")

            await user.add_roles(*[get(ctx.guild.roles, name=team)])
            await ctx.response.send_message(
                f"You've been added to the following roles: {team}"
            )
        except (KeyError, AttributeError) as e:
            await ctx.response.send_message(
                "Sorry, i could not interpret that, try something like /join Cad Team"
            )
            logging.error(e)
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
            user = ctx.user

            logging.info(f"Attempting to remove user from {team}")

            await user.remove_roles(*[get(ctx.guild.roles, name=team)])
            await ctx.response.send_message(
                f"You've been removed from the following roles: {team}"
            )
        except (KeyError, AttributeError) as e:
            await ctx.response.send_message(
                "Sorry, i could not interpret that, try something like /leave CAD Team"
            )
            logging.error(e)
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
        await ctx.send(f"Error! {error}")
        raise error


async def setup(bot):
    await bot.add_cog(SubteamCog(bot))
