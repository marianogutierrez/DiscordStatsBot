# A Bot is a subclass of Client that adds a little bit of extra functionality 
# that is useful when you’re creating bot users. For example, a Bot can 
# handle events and commands, invoke validation checks, and more.
# 
# NOTE: This stats bot file will load and reload user data automatically.
# This data will be obtained from the json that it will load and dump onto.

# statsbot.py
#TODO: Refactor loop to use the on_member_change function instead. This would
# Be more accurate. 
# No need to have locks, but it might be helpful later on to include them
# as if more fucntionality is added, then having locks will
# ensure there are no race conditions. 

# Standard Library Imports 
import os
import logging
import json
import traceback
import time

# Third party Imports
import discord
from discord import activity
from discord.enums import ActivityType
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Local Module imports 
from UserErrorTimer import UserTimer
from GuildMemberStats import GameStats, MemberStatsPack

# Loading environment...
load_dotenv()
TOKEN     = os.getenv('DISCORD_TOKEN')
GUILD     = os.getenv('DISCORD_GUILD')
JSON_FILE = os.getenv('JSON_FILE')
ERR_FILE  = os.getenv('LOG_FILE')

# Setting up logging...
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# For the file handler below, we can use append ('a')to keep over many sessions. 
file_handler = logging.FileHandler(filename=ERR_FILE, encoding='utf-8', mode='w')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Get permissions to see other members on the server. # had .default before
intents_var = discord.Intents.all()

# Use the ! prefix as a command instigator for this bot. 
# Alternatively, a user can simply mention the bot. 
# That will solve the problem if two bots on a server share the same
# command prefix for a bot. 
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), 
                   intents=intents_var, description="The Launched Game Stats Bot!\n"
                   "Command me with my prefix: '!' or via @'ing me!\n"
                   "Example: !<command> [args] or @Launched <command> [args]",
                   help_command=None)

# Variables used by the Bot:
registered_users =  {}
error_dictionary =  {}
hex_color_code = 0x65B460

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
    try:
        if (os.stat(JSON_FILE).st_size == 0) is not True:
            restore_from_json()
    except OSError: 
        logger.error("Failed to find the JSON file that was requested.")

    # Load Cogs
    for file in os.listdir("./Cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"Cogs.{file[:-3]}")

    #record_stats.start() 
# Main tasks below:

def is_user_registered(*, ctx=None, member=None) -> bool:
    """ Helper function:
        Returns true if a user is in a guild given the context.

        The function works with just a discord member passed in,
        or if a user was passed in a mention in a message made 
        from a user, in which case we use the context.
    """
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

            
# @tasks.loop(seconds=15)
# async def record_stats():
#     """ This function is the heart of the bot. We periodically grab data 
#         from the server. The rate can be adjusted, but for now it will be every
#         'X, Y, Z' secs, mins, or hours. A cron job, or an amazon ECS instance 
#         could be used to better manage the uptime of the bot.
#     """
#     guild = discord.utils.get(bot.guilds, name=GUILD)
#     member_list = [member for member in guild.members if member.id in registered_users]
#     for discord_member in member_list:
#         current_user = registered_users[discord_member.id] # User with stats pack
#         # logger.info("Entered for for each loop in member list. "
#         #             "I.e. there exists registered users.")
#         # logger.info("Current Member: " + 
#         #             str(discord_member) + str(discord_member.web_status))
#         # logger.info("User's current activity " 
#         #            + str(discord_member.activity))
#         if (discord_member.activity is not None and discord_member.activity.type 
#                 == discord.ActivityType.playing):
#             current_game = discord_member.activity
#             # Pass datetime in which discord records you started playing. 
#             current_date = current_game.start
#             if current_user.previously_played(current_game.name):
#                 current_user.update_game_stats(current_game, current_date)
#                 record_to_json() 
#                 if current_user.is_game_marked(current_game.name):
#                     game_descript = ("You have launched the marked game: " 
#                                     + current_game.name + "!")
#                     embed_msg = discord.Embed(title="Alert!", 
#                                   description=game_descript,
#                                   color=hex_color_code)

#                     embed_msg.set_thumbnail(url = discord_member.avatar_url)
#                     # The [0] idx is the first text channel found,
#                     # but this can be sent to general chat etc. 
#                     await guild.text_channels[0].send(embed=embed_msg)
#             else:
#                 current_user.init_game_stats(current_game, current_date, False)
#                 record_to_json()

# this begs the question...
# TODO: do I even need the function above if this can do it all? 
# Cases:
# Case 1: No Game -> Game
# Record the stats of the new game: Update or init. Send message if it's marked
# This would count as a launch++
# Case 2: Game -> Other:
# 1.Update game stats if the next item is a game repeating logic from the first case.
# 2. update that game's last time played (regardless). Then call update stats
#    which will verify is it's a new launch. This will need an if not none check!
# 3. If the next item is not a game then we simply ignore it. 
@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    guild = discord.utils.get(bot.guilds, name=GUILD)
    if is_user_registered(before):
        current_user = registered_users[before.id]
        # Case 1: The user has started playing a game.
        if (before.activity == None and (after.activity is not None 
            and after.activity.type == discord.ActivityType.playing)):
                gameobj_after = after.activity
                game_start_date = gameobj_after.start
                if(current_user.previously_played(gameobj_after.name)):
                    # Update the game stats. Provide no end date, since they have 
                    # not gone from resuming playing a game. 
                    current_user.update_game_stats(gameobj_after, game_start_date)
                    record_to_json()
                    if(current_user.is_game_marked(gameobj_after.name)):
                        # The [0] idx is the first text channel found,
                        # but this can be sent to general chat etc. 
                        embed_msg = playing_marked_game(gameobj_after, before)
                        await guild.text_channels[0].send(embed=embed_msg)
                else:
                    # The user is playing a new game
                    current_user.init_game_stats(gameobj_after, 
                                                 game_start_date, False)
                    record_to_json()
        else:  # Case 2: The user is now doing another activity
            # The next activity could be a game!
             if(before.activity is not None and 
                before.activity.type == discord.ActivityType.playing and 
                after.activity is None 
                or after.activity.type == discord.ActivityType.playing):
                users_prev_game = current_user.game_dict[before.activity.name]
                users_prev_game.date_last_played = before.activity.end
                if(after.activity is None):
                    # they stopped playing. Record the time in the db.
                elif after.activity.type = discord.ActivityType.playing:
                    # they started playing. a diff game. Record the time they started playing
                else:
                    pass
            elif (after.activity is not None and after.activity.type
                    == discord.Activity.playing):
                    # record stats of the game they are playing now

                    # record time stopped playing, that is the moment they stopped playing
                    # compare this to the start time of teh game, it would just 
                    # be another date to compare to


def playing_marked_game(game_obj: discord.Game, 
                        member_ref: discord.Member) -> discord.Embed:
    """ Helper function to send an embed notifying the user is playing a game that have
        marked previously! 
    """
    game_descript = ("You have launched the marked game: " 
                      + game_obj.name + "!")
    embed_msg = discord.Embed(title="Alert!", 
                              description=game_descript,
                              color=hex_color_code)

    embed_msg.set_thumbnail(url = member_ref.avatar_url)
    
    return embed_msg

# This function needs to be async, to be blocking. We don't 
# want our lone thread writing to the JSON file, while some other task is
# being awaited!
def record_to_json():
    logger.debug("Attempting to record to JSON")
    with open(JSON_FILE, "w") as json_file:
        json.dump(registered_users, json_file, indent=2, 
                default=MemberStatsPack.json_encoder)


def restore_from_json():
    logger.debug("Attempting to restore from JSON")
    global registered_users
    registered_users_temp = {}

    with open(JSON_FILE, "r") as json_file:
        registered_users_temp = json.load(json_file)
    
    for entry in registered_users_temp:
        registered_users[int(entry)] = None 
        current_entry = registered_users_temp[entry]
        registered_users[int(entry)] = MemberStatsPack.json_decoder(current_entry)


@bot.command(name="getlist", 
            help="Retrieve the games you have previously launched.")
async def get_list(ctx):
    if ctx.author.id in registered_users:
        user_data = registered_users[ctx.author.id]
        game_str = ""
        newline_hit = 0

        for game in user_data.game_dict:
            game_entry = user_data.game_dict[game]
            if newline_hit == 5:
                game_str += '\n'
                newline_hit = 0
            game_str += (str(game_entry.name)) + " | "
            newline_hit += 1

        # Getting embed ready.
        embed_msg = discord.Embed(title=ctx.author.name + "'s" + " Games List", 
                                  description=("The names of the games "
                                  "you've played are below."),
                                  color=hex_color_code)
        embed_msg.set_thumbnail(url = ctx.author.avatar_url)
        embed_msg.add_field(name="Listing", value=game_str)
        await ctx.send(embed=embed_msg)
        
@bot.command(name="markedgames", help="Retrieve "
            "the list of games you have marked.")
async def get_marked_list(ctx):
  if ctx.author.id in registered_users:
        user_data = registered_users[ctx.author.id]
        game_str = ""
        newline_hit = 0

        for game in user_data.game_dict:
            game_entry = user_data.game_dict[game]
            if newline_hit == 5:
                game_str += '\n'
                newline_hit = 0
            if game_entry.marked_game:
                game_str += (str(game_entry.name)) + " "
                newline_hit += 1

        # Getting embed ready.
        msg_title = ctx.author.name + "'s" + " Marked Games List"
        descript = "The names of the games you've marked are below."
        embed_msg = discord.Embed(title=msg_title, 
                                  description=descript,
                                  color=hex_color_code)
        embed_msg.set_thumbnail(url = ctx.author.avatar_url)
        embed_msg.add_field(name="Listing", value=game_str)

        await ctx.send(embed=embed_msg)

@bot.command(name='mark', help="""
Mark a game so that you don't launch it too often.
This argument passed should be the name of the game in quotes if it has spaces.
As displayed on discord. You can view of a list of games by calling
The getlist command too. """)
async def mark(ctx, arg:str):
    logger.info("The game name passed in: " + arg)
    if ctx.author.id in registered_users:
        user = registered_users[ctx.author.id]
        logger.info("user was registered")
        logger.info("the users game_dict length is " + str(len(user.game_dict)))
        if len(user.game_dict) > 0:
            logger.info("user's game list is not empty")
            logger.info("The cond result " + str(arg in user.game_dict))
            if arg in user.game_dict:
                user.game_dict[arg].mark_game(True)
                record_to_json()
            else:
                descript_msg = ("The game you attempted to mark is not in "
                               " your games list If you just started playing, "
                               " the bot will record the Game in a minute!")
                embed_msg = discord.Embed(title="Error!", 
                                  description=descript_msg,
                                  color=hex_color_code)
                embed_msg.set_thumbnail(url = bot.user.avatar_url)
                await ctx.send(embed=embed_msg)


@bot.command(name='unmark', help="""
unmark a previously marked game. If a game was already 
unmarked will do nothing. """)
async def unmark(ctx, arg):
    if ctx.author.id in registered_users:
        user = registered_users[ctx.author.id]
        if len(user.game_dict) > 0: 
            if arg in user.game_dict and user.game_dict[arg].marked_game:
                user.game_dict[arg].mark_game(False)
                record_to_json()
            else:
                embed_descript = ("The game you attempted to mark is not in "
                                 "your games list! If you just started playing,"
                                 " the bot will record the Game a minute!")
                embed_msg = discord.Embed(title="Error!", 
                                        description=embed_descript,
                                        color=hex_color_code)
                embed_msg.set_thumbnail(url = bot.user.avatar_url)
                await ctx.send(embed=embed_msg)

@bot.command(name='register', help='registers yourself with the stats bot.')
async def register_user(ctx):
    """Function that allows a user to register themsevles with the 
       games launched bot. To use the bot, the user must first register
       themselves with it, so that it can begin recording the data of the
       games they have played. 
       
       Example usage: !register OR @<botname> register 
    """

    #TODO: Delete below later for debug. 
    # A user should not be able to register another. 
    mentions = ctx.message.mentions
    if len(mentions) == 1:
        id_to_register = ctx.message.mentions[0].id
        registered_users[id_to_register] = MemberStatsPack()
        record_to_json()
        return
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    user_name_str = ctx.author.name

    if ctx.author.id in registered_users:
        # Prepare embed for previous registration message
        embed_msg = discord.Embed(title="Aready Registered!", 
                                 description="Hi " + user_name_str + "!", 
                                 color=hex_color_code)
        embed_msg.set_thumbnail(url=bot.user.avatar_url)
        embed_msg.add_field(name="Status Report",
                           value='Hi {}, you are already registered in: {}!'
                           .format(ctx.author.name, ctx.guild), inline=True)
        await ctx.author.send(embed=embed_msg)
    else:
        registered_users[ctx.author.id] = MemberStatsPack()
        record_to_json()

        # Prepare embed for first time registration
        embed_msg = discord.Embed(title="Registered!", description="Hi " 
                                 + user_name_str + "!", 
                                 color=hex_color_code)
        embed_msg.set_thumbnail(url = bot.user.avatar_url)
        embed_msg.add_field(name="Status Report", 
                           value='You have been registered in ' + 
                           str(ctx.guild), inline=True)
        await ctx.author.send(embed=embed_msg)

@bot.command(name='deregister', help='deregister yourself from the stats bot.')
async def deregister_user(ctx):
    user_id = ctx.author.id
    if user_id in registered_users:
        del registered_users[user_id]
        del error_dictionary[user_id]
        record_to_json() # Ensure user is not re-added after.

        #Create embed
        embed_msg = discord.Embed(title="Unregistered!", description="",
                                color=hex_color_code)
        embed_msg.set_thumbnail(url = bot.user.avatar_url)
        embed_msg.add_field(name="Goodbye " + ctx.author.name, 
                           value='You have been unregistered in ' 
                           + str(ctx.guild), inline=True)
        await ctx.send(embed=embed_msg)

@bot.command(name='stats', help="""Display the stats of a registered user.
            Apply @user for a particular user. Only one user can be mentioned
            at a time.""")
async def display_stats(ctx):
    logger.debug("Entered the stats function")
    mentions = ctx.message.mentions
    embed_msg = discord.Embed(title=ctx.author.name +  "'s " "Stats", 
                             description="",
                             color=hex_color_code)

    if len(mentions) == 0:
        if ctx.author.id in registered_users:
            embed_msg = report_stats(ctx.author, embed_msg)
            embed_msg.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed=embed_msg)
    elif len(mentions) == 1:
        # The first person mentioned
         logger.debug("entered mentioned but invalid")
         logger.debug(str(ctx.message.mentions[0].id))
         if not is_user_registered(member=ctx.message.mentions[0]):
            descript_msg = "Requested User is not registered"
            not_registered = discord.Embed(title="User not Registered",
                                           description=descript_msg,
                                           color=hex_color_code)
            not_registered.set_thumbnail(url=bot.user.avatar_url)
            await ctx.send(embed=not_registered)
         else:
            embed_msg.title=ctx.message.mentions[0].name +  "'s " "Stats"
            embed_msg.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            embed_msg = report_stats(ctx.message.mentions[0], embed_msg)
            await ctx.send(embed=embed_msg)
    else:
        pass

def report_stats(selected_member: discord.Member, 
                embed: discord.embeds.Embed) -> discord.embeds.Embed:
    """ Helper function for the display_stats displays the main stats for games.
        Parameters:
            selected_member: The member to process stats for.
            embed: An embed that will be modified. 
    """
    user_stats = registered_users[selected_member.id]
    most_launched = user_stats.most_launched_game
    least_launched = user_stats.least_launched_game
    last_launched =  user_stats.last_game_launched

    if (most_launched is None and least_launched is None
            and last_launched is None):
        embed.add_field(name="Error: " , value="No Games Recorded Yet!")
        return embed

    if most_launched is not None:
        embed_helper(field_name="Most Launched Game",
                     game_obj=most_launched, embed=embed)

    if least_launched is not None:
         embed_helper(field_name="Least Launched Game", 
                    game_obj=least_launched, embed=embed)

    if last_launched is not None:
        embed_helper(field_name="Last Launched Game", 
                    game_obj=last_launched, embed=embed)

    return embed

def embed_helper(*, field_name: str, game_obj: GameStats,embed: 
                discord.embeds.Embed) -> discord.embeds.Embed:
    """Helper function to add fields to game stats.
        Parameters:
            field_name: A string that will be used as the name of a new field
                        for an embed.
            game_obj:   An instance of a game object that will be used to 
                        retrieve game data.
            embed:      An instance of a discord embed that will be 
                        modified to add a field.
    """
    embed.add_field(name=field_name,
                    value=game_obj.name
                    + "\nDate First Played: "
                    + str(game_obj.date_first_added)
                    + "\nDate Last Played: "
                    + str(game_obj.date_last_played)
                    + "\nTimes Launched: "
                    + str(game_obj.times_launched)
                    + "\nDays Launched: "
                    + str(game_obj.days_launched),
                    inline=True)


@bot.command(name='isRegi', 
help='Invoke to return a list of users registered with this bot on the server.' )
async def user_registration_status(ctx):
    """ Users invoke this command in the server to see if a user is registered with the
        games launched bot. 

        Usage: !isRegi - will tell the calling user if they are registered
               !isRegi @<user in server> - tell user if requested user is registered
               The above usage can also be invoked by merely mentioning the bot.
    """
    descript = ""
    embed_msg = discord.Embed(title="Registration Status", 
                             description=descript,
                             color=hex_color_code)

    if not is_user_registered(ctx=ctx):
        descript = "The requested user is not registered."
        embed_msg.description = descript
        embed_msg.footer = "Called by " + ctx.author
        await ctx.send(embed=embed_msg)
    else:
        descript = "The requested user is registered."
        embed_msg.description = descript
        await ctx.send(embed=embed_msg)

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
            error_dictionary[ctx.author.id] = UserTimer()
            user = error_dictionary[ctx.author.id]
            user.error_count = 1

            # Get embed ready
            error_descript = ("Invalid command was used. "
                             "Please see the help read out via !help.")
            embed_msg = discord.Embed(title = "Error!", 
                                     description = error_descript,
                                     color = hex_color_code)
            embed_msg.set_thumbnail(url = bot.user.avatar_url)
            await ctx.send(embed=embed_msg)
        elif ctx.author.id in error_dictionary:
            user = error_dictionary[ctx.author.id]
            user.error_count += 1

            # Get embed ready
            error_descript = ("Invalid command was used. "
                             "Please see the help read out via !help.")
            embed_msg = discord.Embed(title = "Error!", 
                                     description = error_descript,
                                     color = hex_color_code)
            embed_msg.set_thumbnail(url = bot.user.avatar_url)

            # If the user hasn't spammed a message in a while, 
            # then restart their error count.
            if (user.time_created + 10 < time.time()) and not user.on_cooldown:
                user.error_count = 1
                user.time_created = time.time()
                await ctx.send(embed=embed_msg)
            # Start the timer when the user has entered more than three
            # Incorrect commands, but check to see that they are not on cooldown.
            elif (user.error_count > 3) and not user.on_cooldown:
                user.start_timer(10) # Hard coded at ten seconds.
                embed_msg.description = ("Too many invalid commands sent. "
                                         "Activating 10 second cool down.")
                await ctx.send(embed=embed_msg)
            # Timer is done. Resume normal behavior.
            elif user.timer_done():
                 user.error_count = 1
                 await ctx.send(embed=embed_msg)
            # First time entry, and already in the error dictionary.
            elif not user.on_cooldown:
                await ctx.send(embed=embed_msg)
            else:
                pass

@bot.event
async def on_error(event, *args, **kwargs):
    if event == 'on_message':
        logger.error(f'Unhandled message: {args[0]}\n')
    else:
        logger.error("Unhandled error " + str(event))
        logger.error(str(traceback.print_exc()))
            
# Kick start / main function
bot.run(TOKEN)