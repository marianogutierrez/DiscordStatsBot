# Discord Cog to create custom help commmand for the stats bot.
import asyncio
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
        # Set the bot, and remove the default help command.
        self.bot = bot
        self.bot.remove_command("help")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Help Cog now Active.")

    @commands.command(name='help', aliases=["h"], 
                      description="The Help Command", help="Call this command "
                      "to receive help on how to use the bot.")
    async def help_command(self, ctx):

        cog_list = sorted([cogs for cogs in self.bot.cogs.keys()])
        page_list = []

        primary_embed = discord.Embed(title="Help Command",
                              description=self.bot.description,
                              color=self.hex_color_code)
        primary_embed.set_thumbnail(url=self.bot.user.avatar_url)

        timeout_embed = discord.Embed(title="Timed out",
                              description="The help message has timed out.",
                              color=self.hex_color_code)
        timeout_embed.set_thumbnail(url=self.bot.user.avatar_url) 

        # The first page is the general help page.
        page_list.append(primary_embed)

        # Process each cog:
        for cog in cog_list:
            command_text = ""
            for command in self.bot.get_cog(cog).walk_commands():
                if command.parent is None and command.hidden == False:
                    command_text += (f"❗{command.name}  - {command.description}\n"
                                     "Help Description: " + f"{command.help}\n"
                                     "=====\n")
            # The Cog's command have been processed, now to add it to the page list.
            title ="Category: " + str(cog)
            description = command_text
            page_list.append(discord.Embed(title=title,description=description,inline=False))

        # Logic to create the pagination inteface below: 

        # Call upon a 'future' object
        # This will send off the message given the context, but also return
        # the message itself. This allows for future modification.
        message = await ctx.send(embed=primary_embed)
        # Setup the buttons we will be using for our message.
        await message.add_reaction('⏮')
        await message.add_reaction('⬅️')
        await message.add_reaction('➡️')
        await message.add_reaction('⏭')

        curr_reaction = None
        total_pages = len(page_list)
        page_idx = 0

        # Declaration of local function with the same arguements as 
        # the reaction_add event. This is necessary in order to use the wait_for call.
        def check(curr_reaction, user):
            return user == ctx.author

        while True:
            if str(curr_reaction) == '⏮':
                page_idx = 0
                await message.edit(embed=page_list[page_idx])
            elif str(curr_reaction) == '⬅️':
                if page_idx > 0:
                    page_idx -= 1
                    await message.edit(embed=page_list[page_idx])
            elif str(curr_reaction) == '➡️':
                if page_idx < total_pages - 1:
                    page_idx += 1
                    await message.edit(embed=page_list[page_idx])
            elif str(curr_reaction) == '⏭':
                page_idx = total_pages - 1
                await message.edit(embed=page_list[page_idx])
            try:
                curr_reaction, user = await self.bot.wait_for('reaction_add', timeout = 30.0, check = check)
                await message.remove_reaction(curr_reaction, user)
            except asyncio.TimeoutError:
                await message.edit(embed=timeout_embed)
                break

        # Once the message has expired, we clear all reactions on the message.
        await message.clear_reactions()

def setup(bot: commands.Bot):
    """ Setup for extension loading.
        Adds the help cog to our Bot.
    """
    bot.add_cog(Help(bot))