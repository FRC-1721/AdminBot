import discord
import logging

from discord import app_commands
from discord.ext import commands
from utilities.image_utils import (
    apply_image_task,
    load_image_from_bytes,
    save_image_to_bytes,
)

from typing import Optional

# Just makes sure we decorate where the image_tasks go, cool python!
import utilities.image_tasks


class ImageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Dynamically create context menus for registered tasks
        self.register_context_menus()

        # All done, bot will sync the whole tree once every cog is loaded
        logging.info("image_cog finished loading.")

    def register_context_menus(self):
        """
        Register context menu commands for all image tasks in the IMAGE_TASKS registry.
        """
        # Import registry here to avoid circular imports
        from utilities.image_utils import IMAGE_TASKS

        for task_name in IMAGE_TASKS:
            # For every task in the IMAGE_TASKS list of registered (decorated tasks)

            # Do a context menu thing (Discord)
            context_menu = app_commands.ContextMenu(
                name=task_name.title(),  # Could be improved, pass a real name here?
                callback=self.process_image_context,
            )

            # Set a custom attribute to track the task name
            context_menu.task_name = task_name

            # Add the context menu command to the bot
            self.bot.tree.add_command(context_menu)

    async def process_image_context(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
    ):
        """
        Generic handler for image context menu tasks. (Stack overflow throw-in)
        """

        task_name = interaction.command.task_name
        await self.process_image_task(task_name, interaction, message)

    async def process_image_task(
        self,
        interaction: discord.Interaction,
        task_name: str,
        message: Optional[discord.Message] = None,
    ):
        """
        Process an image task dynamically.

        - For context menu tasks, `message` is provided.
        - For command tasks, it fetches the message containing the command.
        """

        # If no message is provided, assume it's an interaction (command usage)
        if not message:
            # Try to fetch the most recent message from the interaction channel
            channel = interaction.channel
            async for msg in channel.history(limit=1):
                message = msg
                break

        # If *still* not message lol
        if not message:
            await interaction.response.send_message(
                "Unable to fetch a relevant message to process!", ephemeral=True
            )
            return

        # Ensure the message has an attachment
        if not message.attachments:
            await interaction.response.send_message(
                "This message doesn't have an image attachment!", ephemeral=True
            )
            return

        # Fetch the first attachment
        attachment = interaction.message.attachments[0]
        if not attachment.content_type.startswith("image/"):
            await interaction.response.send_message(
                "The attachment is not an image!", ephemeral=True
            )
            return

        # Fetch the image bytes
        await interaction.response.defer()  # Acknowledge the interaction
        image_bytes = await attachment.read()

        try:
            # Load the image
            input_image = load_image_from_bytes(image_bytes)

            # Apply the task
            output_image = apply_image_task(input_image, task_name)

            # Convert the result to bytes
            output_bytes = save_image_to_bytes(output_image)

            # Send the result
            await interaction.followup.send(
                file=discord.File(io.BytesIO(output_bytes), "result.png")
            )
        except Exception as e:
            logging.error(f"Error processing image task '{task_name}': {e}")
            await interaction.followup.send(
                "Failed to process the image.", ephemeral=True
            )

    @app_commands.command(name="myvote")
    async def myvote_context(self, interaction: discord.Interaction):
        """
        Add a voting frame to the image.
        """
        await self.process_image_task(interaction, "myvote")

    @app_commands.command(name="whiteboard")
    async def whiteboard_context(self, interaction: discord.Interaction):
        """
        Add an image to the whiteboard template.
        """
        await self.process_image_task(interaction, "whiteboard")

    @app_commands.command(name="keegan")
    async def keegan_context(self, interaction: discord.Interaction):
        """
        Keegan's template
        """
        await self.process_image_task(interaction, "keegan")


async def setup(bot):
    await bot.add_cog(ImageCog(bot))
