import discord
from discord.ext import commands
from discord import app_commands

from env import BOT_TEST_SERVER, GFG_SERVER


class Fun(commands.Cog):
    """Fun!"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name='nerd',
        description=''
    )
    @commands.has_permissions(administrator=True)
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def nerd(self, ctx: commands.Context):
        ...


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
