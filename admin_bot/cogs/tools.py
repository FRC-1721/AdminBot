# Tidal Force robotics
# 2021, Admin Bot
# MIT License


import pytz
import discord
import logging
import asyncio
import requests

from discord.ext import commands, tasks
from datetime import datetime, timedelta, time
from ics import Calendar


class ToolCog(commands.Cog, name="Tools"):
    def __init__(self, bot):
        self.bot = bot

        self.status_channel = self.bot.get_channel(590312300695650305)
        self.alert_channel = self.bot.get_channel(634136760401526793)

        # Setup calender
        self.localtz = pytz.timezone("US/Eastern")
        self.upcoming_events.start()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.get_guild(590309936538451972).me.edit(nick="Adman")

        await self.status_channel.send(
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
    async def rtfm(self, ctx, *, member: discord.Member = None):
        """
        Returns the latest infrastructure manual

        Ex: ^rtfm

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

    @commands.command()
    async def get_help(self, ctx, team, *args):
        """
        Requests help from leads or learned members of the team, specified by team

        Ex: ^get_help kode The PID wont fit in the kinematics, so I cant defibrillate the ramsete compiler!

        Written by Khan
        """

        helper_roles = (
            "Kode",
            "Mechanical",
            "Electrical",
            "CAD",
            "Mentor",
            "all",
        )

        if team in helper_roles:
            message = " ".join(args)

            await ctx.send(
                f"```asciidoc\n[HELP TICKET]\n{message}\n------------------\n```"
            )

        else:
            await ctx.send(
                f"Unrecagnized team {team}, please use one of the following:\nKode, Mechanical, Electrical, CAD, Mentor, all"
            )

    @commands.command()
    @commands.has_role("Team Member")
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

    @tasks.loop(minutes=1)  # Still waits for 11:58 though
    async def upcoming_events(self):
        """Drops calender events in the announcements channel"""
        logging.info("Running upcomming events")

        while True:  # Runs forever
            await asyncio.sleep(self.seconds_until(6, 00))  # Wait here till 6am

            embed = self.get_events()

            if embed != None:  # Only post IF theres stuff to send!
                # Check if the last message was posted by us (to prevent double posting)
                last_message = await self.alert_channel.fetch_message(
                    self.alert_channel.last_message_id
                )  # Get last message

                if last_message.author == self.bot.user:
                    logging.info("Last announcement was sent bu us! Deleting it.")
                    await last_message.delete()

                await self.alert_channel.send(embed=embed)  # Send it!
            else:
                logging.info("todays_events: No messages to display today")

            await asyncio.sleep(60)  # So we dont spam while its 11 pm

    def seconds_until(self, hours, minutes):
        """From stackoverflow and coppied by joe but will
        wait for a designated period of time and then resume."""

        given_time = time(hours, minutes, tzinfo=self.localtz)
        now = datetime.now(tz=self.localtz)
        future_exec = datetime.combine(now, given_time)
        if (
            future_exec - now
        ).days < 0:  # If we are past the execution, it will take place tomorrow
            future_exec = datetime.combine(
                now + timedelta(days=1), given_time
            )  # days always >= 0

        logging.debug(
            f"seconds_until: Seconds to wait.. {(future_exec - now).total_seconds()}"
        )
        return (future_exec - now).total_seconds()

    def get_events(self, days=2):
        """
        Returns a list of upcoming events
        """

        cal_url = "https://calendar.google.com/calendar/ical/s6pg5kgtmu98ibee92h5d1gqh0%40group.calendar.google.com/public/basic.ics"  # From google
        teamCal = Calendar(requests.get(cal_url).text)
        events = teamCal.events
        sorted_events = sorted(events, reverse=False)

        # Now
        now = datetime.now()

        # Find today's events
        todays_events = []
        day_search = timedelta(days=days)

        # Add the events that are in the search range
        for event in sorted_events:
            if (
                event.begin.replace(tzinfo=self.localtz)
                > now.replace(tzinfo=self.localtz)
                and event.begin.replace(tzinfo=self.localtz)
                < now.replace(tzinfo=self.localtz) + day_search
            ):
                todays_events.append(event)

        # Remove events with no description
        filtered_events = []
        for event in todays_events:
            try:
                summary = event.summary
                desc = event.description

                logging.debug(f"Len of {desc} is {len(desc)}")
                if len(desc) != 0:
                    filtered_events.append(event)
            except AttributeError:
                summary = "Error fetching summary"

        if len(filtered_events) > 0:
            # We only building a message IF we see that we have stuff to post about!
            embed = discord.Embed(
                title="Upcoming Events",
                url="https://www.frc1721.org/calendar.html",
                color=0xE62900,
            )

            # Set thumbnail
            embed.set_thumbnail(
                url="https://raw.githubusercontent.com/FRC-1721/marketing-material/main/logos/2019/FMS/1721_fms.png"
            )

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
                        name=f"{event.summary} at {event.begin.astimezone(tz=self.localtz).strftime('%-I:%M %p, %A %-d/%-m')}",
                        value=event.description,
                        inline=False,
                    )

            embed.set_footer(text=f"Bot version {self.bot.version}")

            return embed
        else:
            return None  # Return nothing if nothing is happening


async def setup(bot):
    await bot.add_cog(ToolCog(bot))
