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
import time

from typing import Literal, Optional
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from ics import Calendar

from utilities.common import seconds_until


class BatteryCog(commands.Cog, name="Batteries"):
    def __init__(self, bot):
        self.bot = bot

        # Our timezone
        self.localtz = pytz.timezone("US/Eastern")

        # All possible beak statusees
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
                    timestamp bigint,
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
        """Returns all of the possible battery beak statuses"""
        statuses = self.beakStatus
        return [app_commands.Choice(name=status, value=status) for status in statuses]

    async def batteries(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Returns all of the already cataloged batteries"""
        ids = []
        with self.conn.cursor() as cur:
            cur.execute("SELECT DISTINCT id FROM batteryLogs")
            for record in cur:
                ids.append(record[0])
        return [app_commands.Choice(name=record, value=record) for record in ids]

    async def lastStatus(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Returns whatever the last status was"""
        battId = "23A"
        lastStatus = False
        with self.conn.cursor() as cur:
            cur.execute("SELECT DISTINCT comp FROM batteryLogs WHERE id = %s", (battId))
            for record in cur:
                lastStatus = record
        return [app_commands.Choice(name=lastStatus, value=lastStatus)]

    async def trueFalse(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name="Ready", value="True"),
            app_commands.Choice(name="Not Ready", value="False"),
        ]

    @app_commands.command(name="battery_record")
    @commands.has_role("Electrical Team")
    @app_commands.autocomplete(status=beakStatuses)
    @app_commands.autocomplete(battery_id=batteries)
    @app_commands.autocomplete(comp_ready=trueFalse)
    async def battery_record(
        self,
        ctx: discord.Interaction,
        battery_id: str,
        comp_ready: str = None,
        charge_status: float = -1.0,
        int_resistance: float = -1.0,
        memo: str = "N/A",
        status: str = "N/A",
    ):
        """Use this command to add a new record to the battery database!"""

        with self.conn.cursor() as cur:
            # If the comp_ready is not set, just use whatever the last value was defaulting to True.
            if comp_ready == None:
                cur.execute(
                    "SELECT DISTINCT comp FROM batteryLogs WHERE id = %s", (battery_id,)
                )
                prevStatus = cur.fetchone()
                if prevStatus is not None:  # Check if is none
                    comp_ready = prevStatus[0]  # Return whatever previous status
                else:
                    comp_ready = True  # Return default

            cur.execute(
                "INSERT INTO batteryLogs (timestamp, id, comp, beakStatus, beakRInt, beakCharge, note) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    int(time.time()),
                    battery_id,
                    comp_ready,
                    status,
                    charge_status,
                    int_resistance,
                    memo,
                ),
            )

            self.conn.commit()

            cur.execute(
                "SELECT * FROM batteryLogs WHERE id = %s LIMIT 1", (battery_id,)
            )

            await ctx.response.send_message(self.format(cur)[0])

    @app_commands.command(name="battery_info")
    @commands.has_role("Electrical Team")
    @app_commands.autocomplete(battery_id=batteries)
    async def battery_info(self, ctx: discord.Interaction, battery_id: str):
        """Get the history for a specific battery!"""

        rawLog = ""

        with self.conn.cursor() as cur:
            query = "SELECT * FROM batteryLogs WHERE id = %s"
            cur.execute(query, (battery_id,))

            rawLog = self.format(cur)

        if rawLog[1][1]:
            embedColor = 0x00FF00
        else:
            embedColor = 0xE62900

        embed = discord.Embed(
            title=f"Battery {battery_id}",
            color=embedColor,
        )

        embed.add_field(
            name="Condition",
            value=rawLog[1][2],
            inline=True,
        )

        embed.add_field(
            name="Internal Resistance",
            value=rawLog[1][4],
            inline=True,
        )

        embed.add_field(
            name="Competition Ready",
            value=rawLog[1][1],
            inline=False,
        )

        if rawLog != None:
            await ctx.response.send_message(rawLog[0], embed=embed)
        else:
            await ctx.response.send_message(f"No records for battery `{battery_id}`.")

    def format(self, cur):
        """Returns a formatted table with each battery log, otherwise None"""
        if cur.rowcount <= 0:
            return None

        ret = "```\n"
        # Headers for table
        table = [
            (
                "Date",
                "Batt. ID",
                "Comp. Ready",
                "Condition",
                "Charge",
                "Int. Resis.",
                "Memo",
            )
        ]

        for row in [record for record in cur]:
            # Convert timestamp to date.
            date = datetime.fromtimestamp(int(row[0]), tz=self.localtz).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            mutRow = list(row)
            mutRow[0] = date
            table.append(mutRow)

        for record in table:
            ret += f"{record[0]:<22} {record[2]:<12} {record[3]:<12} {record[4]:<10} {record[5]:<12} {record[6]:<20}\n"
        ret += "\n```"

        # Return the latest log as well as the latest record
        return ret, table[-1]


async def setup(bot):
    await bot.add_cog(BatteryCog(bot))
