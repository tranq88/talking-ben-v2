import discord
from discord.ext import commands

from env import BOT_TEST_SERVER, GFG_SERVER


class ErrorHandler(commands.Cog):
    """Handle errors."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self,
                               ctx: commands.Context,
                               error: commands.CommandError):
        if isinstance(error, commands.errors.CommandNotFound):
            return
        await ctx.reply(error)


async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorHandler(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
