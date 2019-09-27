import discord
from discord.ext import commands
from discord.ext.commands import Cog


class Help_Command(Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help_command(self, ctx):
        title = "About PUBGDiscoBot"
        description = ''.join([
            "!IMPORTANT! This bot tracks only STEAM PUBG players\n\n",
            "PUBGDiscoBot made with :hearts: by <@132402729887727616>\n",
            "This is an open-source project. You can find it on ",
            "[GitHub](https://github.com/glmn/PUBGDiscoBot)"])

        embed = discord.Embed(colour=discord.Colour(0x50e3c2),
                              title=title,
                              description=description)
        embed.add_field(name="**How to track player?**", value=''.join([
            'Type **`pubg reg IGN`** where IGN - ',
            'Your ingame nickname\n',
            'Example: ***`pubg reg chocoTaco`***'
        ]), inline=False)
        embed.add_field(name="**Another commands**", value=''.join([
            '**`pubg me`** - Shows your tracked players\n',
            '**`pubg last`** - Shows last game with TOP-3 rank\n',
            '**`pubg help`** - Shows this help message'
        ]), inline=False)
        await ctx.send(content='\u200b', embed=embed)


def setup(bot):
    bot.add_cog(Help_Command(bot))
