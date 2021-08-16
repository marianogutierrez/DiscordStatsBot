# A Bot is a subclass of Client that adds a little bit of extra functionality 
# that is useful when you’re creating bot users. For example, a Bot can 
# handle events and commands, invoke validation checks, and more.
# 
# NOTE: This stats bot file will load and reload user data automatically.
# This data will be obtained from the json that it will load and dump onto.
# All json logic lies in the CoreFunctions.py Cog.

# StatsBot.py

# Standard Library Imports 
import os

# Third party Imports
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Loading environment...
load_dotenv()
TOKEN     = os.getenv('DISCORD_TOKEN')
GUILD     = os.getenv('DISCORD_GUILD')

# Get permissions to see other members on the server. # had .default before
intents_var = discord.Intents.all()

# Flag to ensure that if on_ready calls itself again - which is posible -
# in the event of network retries etc, that it does not load our cogs again.
has_loaded = False

# Use the ! prefix as a command instigator for this bot. 
# Alternatively, a user can simply mention the bot. 
# That will solve the problem if two bots on a server share the same
# command prefix for a bot. 
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), 
                   intents=intents_var, description="The Launched Stats Bot!\n"
                   "Command me with my prefix: '!' or via @'ing me!\n"
                   "Example: !<command> [args] or @Launched <command> [args]",
                   help_command=None)

# The main function to kick off: 
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
   
    # For debugging purposes. 
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

    # Load Cogs
    # The on ready function can be called multiple times...
    # Since this is the case, we should not have to load extensions again and again...
    global has_loaded
    if has_loaded == False:
        for file in os.listdir("./Cogs"):
            if file.endswith(".py") and not file.startswith('__init__'):
                bot.load_extension(f"Cogs.{file[:-3]}")
        has_loaded = True

# Kick start / main function
bot.run(TOKEN)