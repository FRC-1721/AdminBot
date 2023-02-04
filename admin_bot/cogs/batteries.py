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


class BatteryCog(commands.Cog, name="Batteries"):
    def __init__(self, bot):
        self.bot = bot

        self.beakStatus = [
            "Good",
            "Fair",
            "Poor",
        ]

        # Connect to DB
        self.conn = psycopg.connect(
            "dbname=admin_bot_db user=postgres password=postgres host=database"
        )

        # Setup DB
        with self.conn.cursor() as cur:
            # Execute a command: this creates a new table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS batteryLogs (
                    id text,
                    comp boolean DEFAULT TRUE,
                    beakStatus text,
                    beakRInt real,
                    beakCharge real,
                    note text)
                """
            )

            # Commit the db changes!
            self.conn.commit()

    async def beakStatuses(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        statuses = self.beakStatus
        return [app_commands.Choice(name=status, value=status) for status in statuses]

    @app_commands.command(name="record")
    @commands.has_role("Electrical Team")
    @app_commands.autocomplete(status=beakStatuses)
    async def record(
        self,
        ctx: discord.Interaction,
        battery_id: str = "23A",
        memo: str = '"None"',
        status: str = None,
    ):
        """Logs a new battery status!"""

        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO batteryLogs (id, comp, beakStatus, beakRInt, beakCharge, note) VALUES (%s, %s, %s, %s, %s, %s)",
                (battery_id, False, status, 100, 0.1, memo),
            )

            self.conn.commit()

            cur.execute("SELECT * FROM batteryLogs")

            repl = "```\n"
            for record in cur:
                repl += f"{record}\n"
            repl += "\n```"

            await ctx.response.send_message(repl)


async def setup(bot):
    await bot.add_cog(BatteryCog(bot))
