# DiscordStatsBot
## A Discord bot that collects data from the users on the server.

![Launched Banner](https://github.com/marianogutierrez/DiscordStatsBot/blob/main/LaunchedBanner.png)

# What is the "Launched" discord bot?
The launched discord bot keeps track of the games a user has launched i.e. have started playing. 

# What kind of data is collected by the "Launched" discord bot? 
The Launched discord bot begins to collect the most, least, and last launched game. Before this can be done, the user must first register with the bot first. The bot then interacts with the user's via Discord Py's API to determine when they have started playing a new game. Registered users, can then ping the bot to gather there own personal data regarding those three key games (most, least, and last launched).

# What else does this bot do?
The Launched discord bot also has one important feature. This is the abilty to "mark" a game. What this implies is that a user can enter the name of the game (as discord sees it in it's "Playing" status) in quotes to the bot. With this information the bot can then alert the server memeber that they have begun to play a game they did not want to be playing. This bot and the "mark" feature was inspired by a friend who did not want to keep playing a particular game. Keep track of all the stats of the games they have been played, and to be reminded to not play a particular game.

# Technical Details:
This bot records data in a json file. The data structures created for it are designed to be dumped into a file and then restored by parsing the dictionaries in the JSON file. This restores the data structures upon the waking of the bot, so that all data is saved when it is resumed.

# How do I run this bot? 
This bot makes uses of the load dotenv modules see: https://github.com/theskumar/python-dotenv
Loading some data as enviroment variables is necessary, as a bot's TOKEN is unique to the user who created it. Thus, exposing such data in source code would be very unwise, and other users may engage in malicious actions with the bot.

Use of the load env module can be seen in the CoreFunctions cog, as well as the main driver, StatsBot.py.

```
# Loading environment...
load_dotenv()
TOKEN     = os.getenv("DISCORD_TOKEN")
GUILD     = os.getenv("DISCORD_GUILD")
JSON_FILE = os.getenv("JSON_FILE")
ERR_FILE  = os.getenv("LOG_FILE")
```

Overall, the user must have a token - thus they have to make their own bot first - a guild to run the bot, and some hardcoded paths on where there JSON and error files will be located.
Finally, the user should enter the StatsBotPackage, and run `python<3.7 or greater> StatsBot.py`.
