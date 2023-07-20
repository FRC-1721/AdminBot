# Tidal Force robotics
# 2021, Admin Bot
# MIT License


import pytz
import discord
import logging
import asyncio
import psycopg
import requests
import random

from typing import Literal, Optional
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time
from ics import Calendar

from utilities.common import seconds_until


class ToolCog(commands.Cog, name="Tools"):
    def __init__(self, bot):
        self.bot = bot

        # Channels
        self.status_channel = self.bot.get_channel(590312300695650305)
        self.alert_channel = self.bot.get_channel(634136760401526793)

        self.teamServer = self.bot.get_guild(590309936538451972)

        # Setup calender
        self.localtz = pytz.timezone("US/Eastern")
        self.upcoming_events.start()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.teamServer.me.edit(nick="Adman")

        await self.status_channel.send(
            f"Admin Bot version `{self.bot.version}` just restarted."
        )

    @app_commands.command(name="version")
    async def version(self, ctx: discord.Interaction):
        """
        Prints the revision/version.

        Ex: ^version

        Written by Joe.
        """

        await ctx.response.send_message(f"I am running version `{self.bot.version}`.")

    @app_commands.command(name="rtfm")
    async def rtfm(self, ctx: discord.Interaction) -> None:
        """
        Returns the latest infrastructure manual

        Ex: /rtfm

        Written by Joe.
        """

        await ctx.response.send_message(
            f"Find the build space manual here: https://github.com/FRC-1721/infrastructure/releases/latest/download/FRC1721_Infrastructure_Manual.pdf"
        )

    @commands.command()  # Cannot be converted to app command?
    async def feature(self, ctx: discord.Interaction, *args: str) -> None:
        """
        Allows users to request a feature

        Ex: ^feature Give the bot a self destruct command!

        Written by Joe.
        """

        title = "+".join(args)

        await ctx.send(
            f"https://github.com/FRC-1721/AdminBot/issues/new?labels=feature&title={title}&body=Describe+your+feature+here+please!"
        )

    @app_commands.command(name="getlogs")
    async def getlogs(self, ctx: discord.Interaction, lines: int = 10) -> None:
        """
        Gets the last `x` number of lines in the logfile.
        """

        msg = f"```\n last {lines} lines of logs\n\n...\n"
        with open("/tmp/adman.log") as logfile:
            for line in logfile.readlines()[-lines:]:
                msg += line
        msg += "```"
        await ctx.response.send_message(msg)

    @commands.command()
    @commands.has_role("Software Team")
    async def selfdestruct(self, ctx, *args):
        async with ctx.typing():
            await ctx.send(f"Computing...")
            await asyncio.sleep(2)
        await asyncio.sleep(3)
        async with ctx.typing():
            await ctx.send(f"Overloaded...")
            await asyncio.sleep(10)

        async with ctx.typing():
            for i in range(6):
                await ctx.send(f"Overloaded...")
                await asyncio.sleep(0.5)

        quit()

    @app_commands.command(name="today")
    async def today(self, ctx: discord.Interaction) -> None:
        """Gives you today's itinerary!"""

        embed = self.get_events(searchDays=1, showAll=True, embedName="Today's Events")
        if embed != None:  # Only post IF theres stuff to send!
            await ctx.response.send_message(embed=embed)  # Send it!
        else:
            await ctx.response.send_message("Nothing on the calender for today!")

    @app_commands.command(name="tomorrow")
    async def tomorrow(self, ctx: discord.Interaction, days: int = 2) -> None:
        """Gives you tomorrow's itinerary!"""

        embed = self.get_events(
            searchDays=days, showAll=True, embedName="Tomorrow's Events"
        )
        if embed != None:  # Only post IF theres stuff to send!
            await ctx.response.send_message(embed=embed)  # Send it!
        else:
            await ctx.response.send_message("Nothing on the calender for tomorrow!")

    @tasks.loop(minutes=1)  # Still waits for 11:58 though
    async def upcoming_events(self):
        """Drops calender events in the announcements channel"""
        logging.info("Running upcoming events")

        while True:  # Runs forever
            await asyncio.sleep(
                seconds_until(self.localtz, 6, 00)
            )  # Wait here till 6am

            embed = self.get_events()

            if embed != None:  # Only post IF theres stuff to send!
                # Check if the last message was posted by us (to prevent double posting)
                try:
                    last_message = await self.alert_channel.fetch_message(
                        self.alert_channel.last_message_id
                    )  # Get last message

                    if last_message.author == self.bot.user:
                        logging.info("Last announcement was sent bu us! Deleting it.")
                        await last_message.delete()
                except discord.errors.NotFound as e:
                    logging.error(f"Error fetching last message, error: {e}")

                await self.alert_channel.send(embed=embed)  # Send it!
            else:
                logging.info("todays_events: No messages to display today")

            await asyncio.sleep(60)  # So we dont spam while its 11 pm

    def get_events(self, searchDays=2, showAll=False, embedName="Upcoming Events"):
        """
        Returns a list of upcoming events
        """

        cal_url = "https://calendar.google.com/calendar/ical/s6pg5kgtmu98ibee92h5d1gqh0%40group.calendar.google.com/public/basic.ics"  # From google
        teamCal = Calendar(requests.get(cal_url).text)
        events = teamCal.events
        sorted_events = sorted(events, reverse=True)

        # Now
        now = datetime.now(self.localtz)

        # Find today's events
        todays_events = []

        # Add the events that are in the search range
        for event in sorted_events:
            begin = event.begin.replace(tzinfo=self.localtz)

            # Search in range between -2 and +2 days
            if abs((begin - now).days) < searchDays:
                if begin.day - now.day in range(0, searchDays):
                    logging.debug(f"Event {event} on day {begin.day} and day {now.day}")
                    todays_events.append(event)

        # Remove events with no description
        filtered_events = []
        for event in todays_events:
            try:
                summary = event.summary
            except AttributeError:
                event.summary = "Error fetching summary"

            try:
                desc = event.description
            except AttributeError:
                event.description = "Error fetching desc"

            try:
                if len(desc) != 0 or showAll:
                    # If all is true, we'll just add everything in here
                    logging.debug(f"Adding event: {event}")
                    filtered_events.append(event)
            except TypeError:
                # This runs if desc is missing entirely
                logging.error(f"Could not add {desc}")
                if showAll:
                    logging.warn(f"Force adding event: {event}")
                    filtered_events.append(event)

        if len(filtered_events) > 0:
            # We only building a message IF we see that we have stuff to post about!
            embed = discord.Embed(
                title=embedName,
                url="https://www.frc1721.org/calendar.html",
                color=0xE62900,
            )

            # Pick a more fun thumbnail!
            thumbUrl = "https://raw.githubusercontent.com/FRC-1721/marketing-material/main/logos/2019/FMS/1721_fms.png"
            thumbFooter = f"Bot version {self.bot.version}"
            try:
                if self.teamServer is not None and showAll is False:
                    user = random.choice(self.teamServer.members)
                    if len(user.avatar) > 0:
                        thumbUrl = user.avatar
                    if len(user.avatar) > 0:
                        thumbFooter = f"User of the day: {user.display_name}"
                else:
                    logging.error("Error! Could not get guild!")
            except BaseException as error:
                logging.error("Error fetching pfp: {}".format(error))

            # Set thumbnail
            embed.set_thumbnail(url=thumbUrl)

            for event in filtered_events:
                if event.duration >= timedelta(
                    days=1
                ):  # All day events are a lil weird
                    embed.add_field(
                        name=f"{event.summary} all day {(event.begin.astimezone(tz=self.localtz) + timedelta(days=1)).strftime('%A %-d/%-m')}",
                        value=event.description,
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name=f"{event.summary} at {event.begin.astimezone(tz=self.localtz).strftime('%-I:%M %p, %A %-d/%-m')} till {event.end.astimezone(tz=self.localtz).strftime('%-I:%M %p')}",
                        value=event.description,
                        inline=False,
                    )

            embed.set_footer(text=thumbFooter)

            return embed
        else:
            return None  # Return nothing if nothing is happening

    @commands.command()
    @commands.guild_only()
    @commands.has_role("Software Team")
    async def sync(
        self,
        ctx: commands.Context,
        guilds: commands.Greedy[discord.Object],
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        """
        From here https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f
        """
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


async def setup(bot):
    await bot.add_cog(ToolCog(bot))
