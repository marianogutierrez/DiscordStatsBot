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
