""" This module contains a cog for misc features 
    for the Launcher Bot.
"""

# System imports 
import random as random

# Third party imports
import discord
from discord.ext import commands

class Misc(commands.Cog):
    """ A Misc cog that contains commands we can connect to the bot
        that are not pertinent to the core functionality. 
    """
    # Global hex color code for embeds.
    hex_color_code = 0x65B460

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coinflip", description="A command to flip a coin",
                      help="Call to flip a coin! Returns heads or tails")
    async def filp_coin(self, ctx) -> None:
        """ Function that returns 'Heads' or 'Tails' 
            by calling the random function

            Parameters:
                ctx: A discord context object
        """
        coin_filp = random.randint(0,1)
        embed_msg = discord.Embed(title="Coin Flip", 
                                  description="",
                                  color=self.hex_color_code)
        if coin_filp == 1:
            embed_msg.description = "Heads"
            await ctx.send(embed=embed_msg)
        else:
            embed_msg.description="Tails"
            await ctx.send(embed=embed_msg)    

    @commands.command(name="random", description="A random number generator", 
                      help="Return a random number.\n" "Usage: random [lower] "
                      "[upper]")
    async def gen_random_num(self, ctx, 
                            lower_bound:int = 1, upper_bound:int = 10) -> None:
        """ Function that handles a randome number request
            from a guild member.

            Parameters: 
                lower_bound: The lower bound of the range.
                uppper_bound: The upper bound of the range. 
        """
        if upper_bound < lower_bound:
            descript = ("Can't pick a random number if the upper bound is " 
                        "than the lower bound!")
            embed_msg = discord.Embed(title="Error!", 
                                     description=descript,
                                     color=self.hex_color_code)

            await ctx.send(embed=embed_msg)
        else:
            random_num = random.randint(lower_bound, upper_bound)

            title = ("Random Number in range " + str(lower_bound) 
                    + '-' + str(upper_bound))
            embed_msg = discord.Embed(title=title, 
                                     description="Number: " + str(random_num),
                                     color=self.hex_color_code)

            await ctx.send(embed=embed_msg)

def setup(bot: commands.Bot):
    """ Setup for extension loading:
        Adds the Misc Cog to our Bot.
    """
    bot.add_cog(Misc(bot))