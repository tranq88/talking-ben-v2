import discord
from discord.ext import commands
from discord import app_commands

from env import BOT_TEST_SERVER, GFG_SERVER


class Admin(commands.Cog):
    """Administrative commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name='say',
        description=('Make Talking Ben say a message. '
                     '(b!say works better for comedic purposes.)')
    )
    @commands.has_permissions(administrator=True)
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def say(self, ctx: commands.Context, *, message: str):
        if ctx.interaction:
            await ctx.interaction.response.send_message(message)
        else:
            await ctx.message.delete()
            await ctx.channel.send(message)

    @commands.hybrid_command(
        name='purge',
        description='Bulk delete recent messages.'
    )
    @commands.has_permissions(administrator=True)
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def purge(self, ctx: commands.Context, amount: int):
        await ctx.defer(ephemeral=True)
        await ctx.channel.purge(limit=amount + 1)

        if ctx.interaction:
            await ctx.interaction.followup.send(f'Purged {amount} message(s).')


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
