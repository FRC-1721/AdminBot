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

from profanity_check import predict, predict_prob

from utilities.common import seconds_until


# Minimal cog to provide an interface to the digital signage


class InterfaceCog(commands.Cog, name="Interface"):
    def __init__(self, bot):
        self.bot = bot  # Local instance of bot

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
    async def submitPromo(
        self, ctx: discord.Interaction, img: str, days: int, caption: str = None
    ):
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
                    "author": f"Submitted by {ctx.user.nick}",
                    "caption": caption,
                }

                json_object = json.dumps(imgData, indent=4)
                with open(f"{filename}.json", "w") as outfile:
                    outfile.write(json_object)

                # Download the file
                subprocess.run(["wget", img, "-O", f"{filename}.png"])

                await ctx.followup.send(
                    f"Done! Added `{filename}`, expires in `{days}` days! Caption was `{caption}`.",
                    file=discord.File(f"{filename}.png"),
                )
            except Exception as e:
                await ctx.followup.send(f"Sorry! There was an error! {e}")

    @commands.Cog.listener()
    async def on_message(self, ctx: discord.message.Message):
        """
        Pushes messages into the postgresql database.
        """

        # We dont want to publish EVERY channel, just some specific ones!
        allowed_channels = [
            634136760401526793,  # announcements
            590312336414212107,  # mechanical-cad
            1075174212723032064,  # electrical
            590312300695650305,  # software
            776835421976002570,  # outreach-buisness
            1024362276951703552,  # media
            1077252589697126523,  # Quotes
            719692563405078620,  # Joe's testing channel
        ]

        # Check if bot or in pm
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

            if ctx.channel.id in allowed_channels:  # If in allowed channel
                if predict([ctx.content]) == 0:  # If not profanity
                    req = requests.post(  # post
                        url=webhookUrl,
                        data=json.dumps(dataToSend),
                        headers={"Content-type": "application/json"},
                    )
                    logging.debug(f"Sent webhook to signage, req was {req}")
                else:
                    logging.warn(f"Profanity detected in {ctx.content}.")
                    await ctx.add_reaction("⁉️")
            else:
                logging.debug(f"Channel {ctx.channel.id} was not in allowed channels.")


async def setup(bot):
    await bot.add_cog(InterfaceCog(bot))
