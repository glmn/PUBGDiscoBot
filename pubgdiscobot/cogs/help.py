import discord
from pubgdiscobot.config import _version_, _owner_id_, _prefix_
from pubgdiscobot.db import GuildsTable
from discord.ext import commands
from discord.ext.commands import Cog


class HelpCommand(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_guilds = GuildsTable()

    @commands.command(name='help', aliases=['-h', 'commands', 'cmd'])
    @commands.guild_only()
    async def help_command(self, ctx):
        lnk = 'http://x'
        prefix = _prefix_
        if ctx.guild:
            guild_id = ctx.guild.id
            guild = self.db_guilds.find_one({'id': guild_id})
            prefix = guild['prefix']

        title = f"PUBGDiscoBot `v{_version_}` [STEAM ONLY] "
        description = ''.join([
            "PUBGDiscoBot made with :hearts: by <@132402729887727616>\n",
            "This is an open-source project. You can find it on ",
            "**[GitHub](https://github.com/glmn/PUBGDiscoBot)**"])

        embed = discord.Embed(
            colour=discord.Colour(0x50e3c2),
            title=title,
            description=description
        )

        embed.add_field(name="**How to track player?**", value=''.join([
            f'Type [**{prefix}reg IGN**]({lnk}) where IGN - ',
            'Your ingame nickname\n',
            f'Example: [***{prefix}reg chocoTaco***]({lnk})'
        ]), inline=False)

        embed.add_field(name="**Another commands**", value=''.join([
            f'[**{prefix}me**]({lnk}) - Shows your current IGN\n',
            f'[**{prefix}last**]({lnk}) - Shows last analyzed match\n',
            f'[**{prefix}help**]({lnk}) - Shows this help message'
        ]), inline=False)

        if not ctx.author.guild_permissions.administrator:
            await ctx.send(content='\u200b', embed=embed)
            return

        embed.add_field(name="**Admin commands**", value=''.join([
            f'[**{prefix}prefix**]({lnk}) - Set custom prefix for your guild\n',
            f'use brackets to save with space symbol `{prefix}prefix "pubg "`'
        ]))

        if ctx.author.id != _owner_id_:
            await ctx.send(content='\u200b', embed=embed)
            return

        embed.add_field(name="**Owner commands**", value=''.join([
            f'[**{prefix}notify-all**]({lnk}) - Send your message to all guilds\n',
            f'[**{prefix}reload**]({lnk}) - Reload specified extension\n'
        ]))

        await ctx.send(content='\u200b', embed=embed)


def setup(bot):
    bot.add_cog(HelpCommand(bot))
