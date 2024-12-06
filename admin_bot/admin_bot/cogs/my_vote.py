import aiohttp
import discord
import logging

from discord import app_commands
from discord.ext import commands

from PIL import Image, UnidentifiedImageError

from io import BytesIO


class MyVoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Create and add the context menu command
        self.myvote_context_menu = app_commands.ContextMenu(
            name="MyVote",  # The name that appears in the context menu
            callback=self.process_myvote_context,
        )
        self.bot.tree.add_command(self.myvote_context_menu)

        logging.info("Registered context menu command.")

    async def process_myvote_context(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        """
        Context menu callback for the MyVote command.
        """
        # Check if the message contains attachments
        if not message.attachments:
            await interaction.response.send_message(
                "No attachments found in the message!", ephemeral=True
            )
            return

        # Filter the first attachment and ensure it's an image
        attachment = message.attachments[0]
        if not attachment.content_type.startswith("image/"):
            await interaction.response.send_message(
                "The first attachment is not an image!", ephemeral=True
            )
            return

        # Download the image into memory
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    await interaction.response.send_message(
                        "Failed to download the image!", ephemeral=True
                    )
                    return
                image_bytes = await resp.read()

        # Process the image in memory
        try:
            input_image = Image.open(BytesIO(image_bytes))
            output_image = self.create_vote_image(input_image)

            # Send the generated image as a response
            buffer = BytesIO()
            output_image.save(buffer, format="PNG")
            buffer.seek(0)
            await interaction.response.send_message(
                file=discord.File(buffer, filename="myvoteout.png")
            )

        except UnidentifiedImageError:
            await interaction.response.send_message(
                "Error opening the provided image!", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Unexpected error occurred: {e}", ephemeral=True
            )

    def create_vote_image(self, input_image: Image.Image) -> Image.Image:
        """
        Creates a MyVote-styled image in memory.
        """
        # Open the vote frame
        frame = Image.open("admin_bot/resources/vote.png")

        # Resize and position the input image on the frame
        input_image = input_image.resize((375, 250))
        frame.paste(input_image, (40, 240))

        return frame

    async def cog_unload(self):
        """Remove the context menu command when the cog is unloaded."""
        self.bot.tree.remove_command(
            self.myvote_context_menu.name, type=discord.AppCommandType.message
        )


async def setup(bot):
    await bot.add_cog(MyVoteCog(bot))
