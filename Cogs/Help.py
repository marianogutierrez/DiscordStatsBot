# Discord Cog to create custom help commmand for the stats bot.

# Third party imports
import discord
from discord.ext import commands

class Help(commands.Cog):
    """ A Cog that implements a custom help command for the stats bot
        discord bot.
    """
    # Global hex color code for embeds.
    hex_color_code = 0x65B460

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.remove_command("help")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Noted that the help cog is now active.")

    # NOTE: Will need to make this work with the non cogs stats
    # bot.py above all else!!!
    # 
    @commands.command(name='help', aliases=["h"], 
                      description="Help Command Details", help="Call this command "
                      "to receive help on how to use the bot.")
    async def help_command(self, ctx):
        embed_msg = discord.Embed(title="Help Command",
                              description=self.bot.description,
                              color=self.hex_color_code)
        embed_msg.set_thumbnail(url=self.bot.user.avatar_url)

        # Grab the names of cogs we have for this bot. 
        cog_list = [cogs for cogs in self.bot.cogs.keys()]
        # Process each cog
        for cog in cog_list:
            command_text = ""
            for command in self.bot.get_cog(cog).walk_commands():
                if command.parent is None and command.hidden == False:
                    command_text += (f"❇️ {command.name}  - {command.description}\n"
                                     "Help Description: " + f"{command.help}\n"
                                     "--------------------------------------\n")

            embed_msg.add_field(name="Category: " + cog, value=command_text, inline=False)

            print("Added all the cogs in the cog list.")
        await ctx.send(embed=embed_msg)

        print("sent the first mf, now why doenst the next work?")
        embed_msg2 = discord.Embed(title="Help Command",
                            description=self.bot.description,
                            color=self.hex_color_code)
        embed_msg2.set_thumbnail(url=self.bot.user.avatar_url)


        # Process the statsbot file i.e. outside of any cogs.
        bot_command_text = ""
        bot_command_list = [command for command in self.bot.walk_commands()]

        for command in bot_command_list:
            if command.parent is None and command.hidden == False:
                bot_command_text += (f"{command.description}\n"
                                    "Help Description: " + f"{command.help}\n"
                                    "--------------------------------------\n")

                embed_msg2.add_field(name=command.name, value=bot_command_text, inline=False)
                bot_command_text = ""
              
        await ctx.send(embed=embed_msg2)


def setup(bot: commands.Bot):
    """ Setup for extension loading.
        Adds the help cog to our Bot.
    """
    bot.add_cog(Help(bot))