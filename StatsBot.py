# A Bot is a subclass of Client that adds a little bit of extra functionality 
# that is useful when you’re creating bot users. For example, a Bot can 
# handle events and commands, invoke validation checks, and more.
# 
# NOTE: This stats bot file will load and reload user data automatically.
# This data will be obtained from the json file that it will load and dump
# onto. 

# StatsBot.py

# Standard Library Imports 
import os
import logging
import json
import traceback

# Third party Imports
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Local Module imports 
from Cogs.MiscFeatures import Misc
from UserErrorTimer import UserTimer
from GuildMemberStats import MemberStatsPack

# Loading environment...
load_dotenv()
TOKEN     = os.getenv('DISCORD_TOKEN')
GUILD     = os.getenv('DISCORD_GUILD')
JSON_FILE = os.getenv('JSON_FILE')
ERR_FILE  = os.getenv('ERR_FILE')

# Setting up logging...
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=ERR_FILE, encoding='utf-8', mode='w') # OR append to keep over many sessions. 
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents           = discord.Intents.all() # Get permissions to see other members on the server. # had .default before
intents.members   = True   # Be able to see who is on the server.
intents.presences = True  # Be able to see the activites each member is doing

# Use the ! prefix as a command instigator for this bot. 
# Alternatively, a user can simply mention the bot. 
# That will solve the problem if two bots share the same
# command prefix for a bot. 
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

# Variables used by the Bot:
registered_users =  {}
error_dictionary =  {}

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


    # Load data structures with json file data, if the data is available
    # If a user unregistered them selves, they should no longer be part of the json
    if not (os.stat(JSON_FILE).st_size == 0):
        restore_from_json()

    bot.add_cog(Misc(bot))
    record_stats.start() # Begin recording

# Main tasks below: 

@bot.command(name="embed", help= "")
async def embed_test(ctx):
    embed = discord.Embed(title='Example test', description="Test", color=discord.Colour.dark_green())
    embed .add_field(name='test name', value='name', inline=True)
    await ctx.send(embed=embed)

def is_user_registered(ctx = None, member = None) -> bool:
    ''' Returns true if a user is in a guild given the context. 

        The function works with just a discord member passed in,
        or if a user was passed in a mention in a message made 
         from a user.
    '''
    if member is not None:
        if member.id in registered_users:
            return True
        else: 
            return False

    if ctx is not None:
        userlookup_id = ctx.message.mentions[0].id
        if userlookup_id not in registered_users:
            return False
        return True

@tasks.loop(seconds=15)
async def record_stats():
    """ This function is the heart of the bot. We periodically grab data from the server
        The rate can be adjusted, but for now it will be every 'X, Y, Z' secs, mins, hours. 
        A cron job, or an amazon ECS instance could be used to better manage the 
        uptime of the bot.
    """
    guild = discord.utils.get(bot.guilds, name=GUILD)
    member_list = [member for member in guild.members if member.id in registered_users]
    for discord_member in member_list:
        current_user = registered_users[discord_member.id] # User with stats pack
        logger.debug("Entered for for each loop in member list. I.e. there exists registered users.")
        logger.debug("Current Member: " + str(discord_member) + str(discord_member.web_status))
        if discord_member.web_status == discord.Status.online:
            logger.debug("User is not on mobile and is online\n Current Activity: " + discord_member.activity)
            if discord_member.activity is not None and discord_member.activity.type == discord.ActivityType.playing:
                current_game = discord_member.activity
                # Pass datetime in which discord records you started playing. 
                current_date = current_game.start
                print(str(current_date)) #retruns none sometimes
                if current_user.previously_played(current_game.name): #worked 
                    logger.debug("Updating a prexisitng game")
                    current_user.update_game_stats(current_game, current_date) # All is well for this function
                    record_to_json() 
                else:
                    logger.debug("Init newly found game.")
                    current_user.init_game_stats(current_game, current_date, False)  # All is well on init
                    record_to_json()


# This should never be called outside of record stats()
# https://stackoverflow.com/questions/13949637/how-to-update-json-file-with-python
def record_to_json():
    try:
        with open(JSON_FILE, "w") as json_file:
            json.dump(registered_users, json_file, indent=2, default=MemberStatsPack.json_encoder)
    except OSError:
            logging.exception()
    
def restore_from_json():
    global registered_users
    registered_users_temp = {}
    try:
        with open(JSON_FILE, "r") as json_file:
            registered_users_temp = json.load(json_file)
        
        for entry in registered_users_temp:
            registered_users[int(entry)] = "" # Load the keys, i.e. user id's 
            current_entry = registered_users_temp[entry] # MemberStatsPack Dictionary
            registered_users[int(entry)] = MemberStatsPack.json_decoder(current_entry)

    except OSError:
        logger.debug("Failed to open the json file to restore from JSON!")
        logger.debug("Returning as normal without previous saved data.")



@bot.command(name='mark', help="""
mark a game so that you don't launch it too often.
This argument passed should be the name of the game.
As displayed on discord. """)
async def marker(ctx, arg):
    if ctx.author.id in registered_users:
        user = registered_users[ctx.author.id]
        if len(user.game_list) > 0: 
            user.game_list[arg].mark_game(True)

# Function to register the user.
@bot.command(name='register', help='registers yourself with the stats bot.')
async def register_user(ctx):
    # User already registered? Fine, just prompt a message.

    #TODO: Delete this, it's just for debug
    mentions = ctx.message.mentions
    print('in here')
    if len(mentions) == 1:
        id_to_register = ctx.message.mentions[0].id
        registered_users[id_to_register] = MemberStatsPack()

    if ctx.author.id in registered_users:
        await ctx.author.send('Hi {}, you are already registered in: {} !'
        .format(ctx.author.name, ctx.guild))
    else:
        registered_users[ctx.author.id] = MemberStatsPack()
        await ctx.author.send('You are registered')

@bot.command(name='deregister', help='deregister yourself from the stats bot.')
async def deregister_user(ctx):
    user_id = ctx.author.id
    if user_id in registered_users:
        del registered_users[user_id]
        await ctx.author.send('User: ' + ctx.author + 'has been removed from the stats bot')


# bottom two NOTE: are buggy 
@bot.command(name='stats', help=''' Display the stats of a registered user.
            Apply @user for a particular user. Only one user can be mentioned
            at a time.''')
async def display_stats(ctx):
    mentions = ctx.message.mentions
    if len(mentions) == 0:
        # report back the caller's stats, first check if they are registered.
        # send back data 
        print('no mentions')
        if ctx.author.id in registered_users:
            stat_list = report_stats(ctx.author)
            await ctx.send("\n".join(str(stat_list)))

    elif len(mentions) == 1:
         print("user is: " + ctx.message.mentions[0].id) # The first person mentioned
         if not is_user_registered(ctx.message.mentions[0].id):
            await ctx.send('The user is not registered')
         else:
            stat_list = report_stats(ctx.message.mentions[0])
            await ctx.send("\n".join(str(stat_list)))


def report_stats(selected_member: discord.Member):
    print("reporting stats ")
    user_stats = registered_users[selected_member.id]
    stats = [] # per game
    for game in user_stats.game_list:
        curr_stats = [] # new list each time
        curr_stats.append(user_stats.get_most_launched_game())
        curr_stats.append(user_stats.get_least_launched_game())
        curr_stats.append(user_stats.last_launched_game())
        stats.append(curr_stats)
    
    return stats

     
@bot.command(name='isRegi', 
help='Invoke to return a list of users registered with this bot on the server.' )
async def user_registration_status(ctx):
    """ Users invoke this command in the server. 
        This is not for application programming use
    """
    if not is_user_registered(ctx = ctx):
        await ctx.send("The reqeusted user is not registered.")
    else:
        await ctx.send("`The requested user is registered.`")

# We could also just have it so it displays just once for the user again?
# the 10 second cool down thing is kinda stupid. What's the point? We could also just
# Silence it completely.
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
        logger.info("User:" + ctx.author + " attempted to use cmd with improper role.")
    elif isinstance(error, commands.CommandNotFound):
        # If the user is not registered with the bot, then do nothing. 
        if ctx.author.id not in registered_users:
            return
        # User in not yet in the dictionary
        elif ctx.author.id not in error_dictionary:
            print('entered not in dictionary yet')
            error_dictionary[ctx.author.id] = UserTimer()
            user = error_dictionary[ctx.author.id]
            user.error_count = 1
            await ctx.send('`Invalid command was used. Please see the help read out via !help.`')
        elif ctx.author.id in error_dictionary:
            user = error_dictionary[ctx.author.id]
            user.error_count += 1
            if user.error_count > 3 and not user.get_on_cooldown():
                user.start_timer(10)
                await ctx.send('`Too many invalid commands sent. Activating 10 second cool down.`')
            elif user.timer_done():
                 user.error_count = 1
                 await ctx.send('`Invalid command was used. Please see the help read out via !help.`')
            elif not user.get_on_cooldown():
                await ctx.send('`Invalid command was used. Please see the help read out via !help.`')
            else:
                pass # All states covered.
                
@bot.event
async def on_error(event, *args, **kwargs):
    with open(ERR_FILE, 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
    logger.exception() # Include traceback in file. 

# Kick start / main function
bot.run(TOKEN)