# Tidal Force robotics
# 2021, Admin Bot
# MIT License


import os
import time
import json
import pytz
import string
import random
import discord
import logging
import asyncio
import requests
import subprocess

from typing import Literal, Optional
from discord import app_commands
from discord.ext import commands, tasks
from ics import Calendar

from PIL import Image, ImageDraw, ImageFilter, UnidentifiedImageError

from utilities.common import seconds_until


# Minimal cog to provide an interface to the digital signage


class InterfaceCog(commands.Cog, name="Interface"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear_promo")
    @commands.has_any_role("Leads", "Adult Mentor", "Student Mentor")
    async def clearPromo(self, ctx: discord.Interaction):
        """
        Removes all promo materials in rotation
        """
        msg = "Removing: "

        dir = "/app/promo"
        for f in os.listdir(dir):
            msg += f"{f}, "
            os.remove(os.path.join(dir, f))

        await ctx.response.send_message(msg)

    @app_commands.command(name="submit_promo")
    @commands.has_any_role("Leads", "Adult Mentor", "Student Mentor")
    async def submitPromo(self, ctx: discord.Interaction, img: str, days: int):
        """
        Submits a promotional image to be displayed in rotation.
        """

        if days > 90:
            await ctx.response.send_message(
                "Sorry, thats too long for a submitted image to be in rotation. Contact <@&614313406345904148> to submit a permanent promo image."
            )
        else:
            # This may take a moment
            await ctx.response.defer()
            try:
                # Make a random string
                _rand = "".join(
                    random.choices(string.ascii_lowercase + string.digits, k=7)
                )
                # Create a full filename
                filename = f"/app/promo/{(ctx.user.nick).replace(' ', '_')}_{_rand}"

                # Write metadata first
                imgData = {
                    "expires": f"{int(time.time()) + (86400*days)}",
                }

                json_object = json.dumps(imgData, indent=4)
                with open(f"{filename}.json", "w") as outfile:
                    outfile.write(json_object)

                # Download the file
                subprocess.run(["wget", img, "-O", f"{filename}.png"])

                await ctx.followup.send("Done!")
            except Exception as e:
                await ctx.followup.send(f"Sorry! There was an error! {e}")

    @commands.Cog.listener()
    async def on_message(self, ctx: discord.message.Message):
        """
        Pushes messages into the postgresql database.
        """

        # We dont want to publish EVERY channel, just some specific ones!
        allowed_channels = [
            719692563405078620,  # Bot Dev
            590309937125523488,  # General
            590309937125523488,
            590312336414212107,
            1075174212723032064,
            590312300695650305,
            1024362276951703552,
            849996840186675201,
            634136760401526793,
            1077252589697126523,
        ]

        if (
            not isinstance(ctx.channel, discord.channel.DMChannel)
            and not ctx.author.bot
        ):
            logging.info(
                f"Sending message from {ctx.channel.id}, author was {ctx.author.name}, forwarding it!"
            )

            webhookUrl = "http://interface:8000/dashboard/hook"

            dataToSend = {
                "channel": ctx.channel.name,
                "author": ctx.author.display_name,
                "author_avatar": str(ctx.author.avatar.url),
                "content": ctx.content,
                "version": self.bot.version,
            }

            if ctx.channel.id in allowed_channels:
                req = requests.post(
                    url=webhookUrl,
                    data=json.dumps(dataToSend),
                    headers={"Content-type": "application/json"},
                )
                logging.debug(f"Sent webhook to signage, req was {req}")
            else:
                logging.debug(f"Channel {ctx.channel.id} was not in allowed channels.")


async def setup(bot):
    await bot.add_cog(InterfaceCog(bot))