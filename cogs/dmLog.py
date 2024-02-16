import discord
from discord.ext import commands
import logging

class DMLogCog(commands.Cog):
    """
    A simple cog that logs all direct messages sent to the bot and the bot's responses.
    """

    def __init__(self, bot):
        self.bot = bot

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('discord')

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Event that triggers when a message is sent to the bot.

        Args:
            message (discord.Message): The message object for the event.

        Returns:
            None
        """
        # Check if the message is a direct message
        if isinstance(message.channel, discord.DMChannel):
            # Log the message
            self.logger.info(f'User: {message.author.name}, Message: {message.content}')

async def setup(bot):
    await bot.add_cog(DMLogCog(bot))