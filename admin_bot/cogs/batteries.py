# Tidal Force robotics
# 2021, Admin Bot
# MIT License


import pytz
import discord
import logging
import asyncio
import psycopg
import requests
import subprocess
import random
import time
import csv

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
            "Bad",
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
                    author text,
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
                "INSERT INTO batteryLogs (timestamp, id, comp, beakStatus, beakRInt, beakCharge, author, note) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    int(time.time()),
                    battery_id,
                    comp_ready,
                    status,
                    charge_status,
                    int_resistance,
                    ctx.user.nick,
                    memo,
                ),
            )

            self.conn.commit()

            cur.execute(
                "SELECT * FROM batteryLogs WHERE id = %s ORDER BY timestamp DESC LIMIT 1",
                (battery_id,),
            )

            await ctx.response.send_message(self.discordFormat(cur)[0])

    @app_commands.command(name="battery_info")
    @commands.has_role("Electrical Team")
    @app_commands.autocomplete(battery_id=batteries)
    async def battery_info(self, ctx: discord.Interaction, battery_id: str):
        """Get the history for a specific battery!"""

        rawLog = ""

        with self.conn.cursor() as cur:
            query = (
                "SELECT * FROM batteryLogs WHERE id = %s ORDER BY timestamp ASC LIMIT 5"
            )
            cur.execute(query, (battery_id,))

            rawLog = self.discordFormat(cur)

        if rawLog is not None:
            if rawLog[1][2]:
                embedColor = 0x00FF00
            else:
                embedColor = 0xE62900

            embed = discord.Embed(
                title=f"Battery {battery_id}",
                color=embedColor,
            )

            embed.add_field(
                name="Condition",
                value=rawLog[1][3],
                inline=True,
            )

            embed.add_field(
                name="Internal Resistance",
                value=rawLog[1][5],
                inline=True,
            )

            embed.add_field(
                name="Competition Ready",
                value=rawLog[1][2],
                inline=False,
            )

            embed.set_footer(text=f"Bot version {self.bot.version}")

            await ctx.response.send_message(rawLog[0], embed=embed)
        else:
            await ctx.response.send_message(f"No records for battery `{battery_id}`.")

    @app_commands.command(name="battery_purge")
    @commands.has_role("Electrical Team")
    async def battery_purge(self, ctx: discord.Interaction, battery_id: str):
        """Removes all records of a battery, you probably don't want to use this!"""

        backup = self.makeExport(battery_id)

        with self.conn.cursor() as cur:
            query = "DELETE FROM batteryLogs WHERE id = %s"
            cur.execute(query, (battery_id,))

            await ctx.response.send_message(
                f"Deleted all records for battery `{battery_id}`.",
                file=discord.File(backup),
            )

            self.conn.commit()

    @app_commands.command(name="battery_export")
    @commands.has_role("Electrical Team")
    @app_commands.autocomplete(battery_id=batteries)
    @app_commands.choices(
        format=[
            app_commands.Choice(name="CSV", value=1),
            app_commands.Choice(name="PDF", value=0),
        ]
    )
    async def battery_export(
        self, ctx: discord.Interaction, battery_id: str, format: int = 0
    ):
        """Export an entire battery's history as a .csv or .pdf"""

        if format:
            await ctx.response.send_message(
                file=discord.File(self.makeExport(battery_id))
            )
        else:
            with open("admin_bot/resources/battery_report.tex") as inF:
                filedata = inF.read()

                filedata = filedata.replace("VERSION", self.bot.version)
                filedata = filedata.replace(
                    "TITLE",
                    f"Automated battery report for battery \\textbf{{battery_id}}.",
                )
                filedata = filedata.replace("BATTERYID", battery_id)

                texName = f"/tmp/battery_report_{battery_id}.tex"

                with open(texName, "w") as outF:
                    outF.write(filedata)

                self.makeExport(battery_id)

                subprocess.run(["pdflatex", "--output-directory=/tmp", texName])
                await ctx.response.send_message(
                    file=discord.File(f"/tmp/battery_report_{battery_id}.pdf")
                )

    @app_commands.command(name="battery_overview")
    @commands.has_role("Electrical Team")
    @app_commands.choices(
        format=[
            app_commands.Choice(name="CSV", value=1),
            app_commands.Choice(name="PDF", value=0),
        ]
    )
    async def battery_overview(self, ctx: discord.Interaction, format: int = 0):
        """Export an overview of every battery as a .csv or .pdf"""

        if format:
            await ctx.response.send_message(file=discord.File(self.makeOverview()))
        else:
            with open("admin_bot/resources/battery_report.tex") as inF:
                filedata = inF.read()

                filedata = filedata.replace("VERSION", self.bot.version)
                filedata = filedata.replace(
                    "TITLE",
                    f"Automated battery overview.",
                )
                filedata = filedata.replace("BATTERYID", "overview")

                texName = f"/tmp/battery_overview.tex"

                with open(texName, "w") as outF:
                    outF.write(filedata)

                self.makeOverview()

                subprocess.run(["pdflatex", "--output-directory=/tmp", texName])
                await ctx.response.send_message(
                    file=discord.File(f"/tmp/battery_overview.pdf")
                )

    def makeExport(self, battery_id):
        # Yes i know this is vulnerable to injection, stfu
        with open(f"/tmp/battery_{battery_id}.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, quotechar="|")

            with self.conn.cursor() as cur:
                query = "SELECT * FROM batteryLogs WHERE id = %s ORDER BY timestamp ASC"

                # Iter all records
                cur.execute(query, (battery_id,))
                table = self.makeTable(cur)
                for row in table:
                    cleanRow = list(row)
                    cleanRow[-1] = "{" + cleanRow[-1] + "}"
                    writer.writerow(cleanRow)

        return f"/tmp/battery_{battery_id}.csv"

    def makeOverview(self):
        # Yes i know this is vulnerable to injection, stfu
        with open(f"/tmp/battery_overview.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, quotechar="|")

            battery_ids = []
            table = []

            with self.conn.cursor() as cur:
                # Fetch every ID
                cur.execute("SELECT DISTINCT id FROM batteryLogs")
                for record in cur:
                    battery_ids.append(record[0])

                query = "SELECT * FROM batteryLogs WHERE id = %s ORDER BY timestamp DESC LIMIT 1"

                # Iter all records
                for battery_id in battery_ids:
                    cur.execute(query, (battery_id,))
                    table += self.makeTable(cur)
                    for row in table:
                        cleanRow = list(row)
                        cleanRow[-1] = "{" + cleanRow[-1] + "}"
                        writer.writerow(cleanRow)

        return f"/tmp/battery_overview.csv"

    def makeTable(self, cur):
        # Headers for table
        table = [
            (
                "Date",
                "Batt. ID",
                "Comp. Ready",
                "Condition",
                "Charge",
                "Int. Resis.",
                "User",
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

        return table

    def discordFormat(self, cur):
        """Returns a formatted table with each battery log, otherwise None"""
        if cur.rowcount <= 0:
            return None

        ret = "```\n"

        table = self.makeTable(cur)

        for record in table:
            ret += f"{record[0]:<22} {record[2]:<12} {record[3]:<12} {record[4]:<10} {record[5]:<12} {record[6]:<14} {record[7]:<20}\n"
        ret += "\n```"

        # Return the latest log as well as the latest record
        return ret, table[-1]


async def setup(bot):
    await bot.add_cog(BatteryCog(bot))
