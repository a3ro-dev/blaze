import subprocess
subprocess.run('pip install -r requirements.txt', shell=True)
import os
import discord
from discord.ext import commands
import config as cfg
import psutil
import random
import asyncio
from pretty_help import PrettyHelp

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(case_insensitive=True,
                        command_prefix=commands.when_mentioned_or(cfg.PREFIX),
                        intents=intents,
                        owner_ids=[905658967005495356],
                        help_command=PrettyHelp())

bot = Bot()

@bot.event
async def on_ready():
    await bot.wait_until_ready()  # Wait until the bot is ready
    print(f'Logged in as {bot.user.name} | {bot.user.id}') #type: ignore
    print(f'Discord.py API version: {discord.__version__}')
    print(f'Successfully logged in and booted...!')
    await bot.load_extension('jishaku')  # Add the 'await' keyword here

    print("Now loading cogs!")
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{file[:-3]}')
                print(f'Loaded {file[:-3]}')
            except Exception as e:
                print(f'Failed to load {file[:-3]} because: {str(e)}')

async def update_presence():
    while True:
        # Get memory usage and CPU usage
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=None)

        # Create the name list with the number of members in the guild at the 2nd index
        name = [
            f"Memory: {memory_usage:.1f}% | CPU: {cpu_usage:.1f}%",
            f"Order bots on a3ro.xyz",
            f"Helping Moderators",
            f"Greeting my New Friends",
        ]

        # Set the presence with memory and CPU usage info
        await bot.change_presence(
            activity=discord.Streaming(
                name=random.choice(name),
                url="https://www.twitch.tv/",
            )
        )

        # Wait for 5 seconds before updating the presence again
        await asyncio.sleep(5)

bot.run(cfg.TOKEN)