# Launched
### A Discord bot that collects data from the users on the server.

![Launched Banner](https://github.com/marianogutierrez/DiscordStatsBot/blob/main/LaunchedBanner.png)

## What is the "Launched" discord bot?
The launched discord bot keeps track of the games a user has launched i.e. have started playing. 

## What kind of data is collected by the "Launched" discord bot? 
The Launched discord bot begins to collect the most, least, and last launched game. Before this can be done, the user must first register with the bot first. The bot then interacts with the user's via Discord Py's API to determine when they have started playing a new game. Registered users, can then ping the bot to gather there own personal data regarding those three key games (most, least, and last launched).

## What else does this bot do?
In brief, this bot keep tracks of all the stats of the games they have been played, and to be reminded to not play a particular game.
To be more specific, the Launched Discord Bot has abilty to "mark" a game. What this implies is that a user can enter the name of the game (as discord sees it in its "Playing" status) in quotes to the bot. With this information the bot can then alert the server member that they have begun to play a game they did not want to be playing. This bot and the "mark" feature was inspired by a friend who did not want to keep playing a particular game.

## Technical Details:
This bot records data in a json file. The data structures created for it are designed to be dumped into a file and then restored by parsing the dictionaries in the JSON file. This restores the data structures upon the waking of the bot, so that all data is saved when it is resumed.

## How do I run this bot? 
This bot makes uses of the load dotenv modules see: https://github.com/theskumar/python-dotenv
Loading some data as enviroment variables is necessary, as a bot's TOKEN is unique to the user who created it. Thus, exposing such data in source code would be very unwise, and other users may engage in malicious actions with the bot.

Use of the load env module can be seen in the CoreFunctions cog, as well as the main driver, StatsBot.py.

## Inprovements?
During the development of this project, I intended to gain proficency in python and working with the discord API. JSON is something used often and so I wanted to be come proficient in that as well. That being said, a simple text file as the database is not ideal. A SQL or NoSQL db for faster iteration if the data changes. 

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

## The Bot in Action:
### The Help Command:
![Help Command](https://media.giphy.com/media/4Xf0EygOn9tPROTXKc/giphy.gif?cid=790b761116064157663769ed32a90732f88d8d46de9eeb1a&rid=giphy.gif&ct=g)

### Call upon your own stats:
<img src="https://imgur.com/F8va2vZ.png" width="500">

### Or, call upon a friend's:
<img src="https://imgur.com/ZJ4tG4K.png" width="500">

### Ask for Random Numbers:
<img src="https://imgur.com/SATfwe6.png" width="500">

### Notify the server you're playing something you marked!
<img src="https://imgur.com/FwT5UDL.png" width="500">
