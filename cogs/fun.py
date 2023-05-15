import discord
from discord.ext import commands
from discord import app_commands

from env import BOT_TEST_SERVER, GFG_SERVER, GFG_NSFW_ID

from datetime import datetime
import pytz


class Fun(commands.Cog):
    """Fun!"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name='nerd',
        description='Send a nerd speech bubble. Also works as a reply.'
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def nerd(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.send_message(
                "Use b!nerd instead (i'm too lazy to implement this one)",
                ephemeral=True
            )
            return

        nerd = discord.File('assets/nerd.mp4')

        if ctx.message.reference:
            r = await ctx.channel.fetch_message(
                ctx.message.reference.message_id
            )
            await r.reply(
                file=nerd,
                mention_author=False
            )
        else:
            await ctx.channel.send(file=nerd)

        await ctx.message.delete(delay=0.5)

    @commands.hybrid_command(
        name='ballout',
        description="IT'S FRIDAY. BALL OUT!"
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def ballout(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.send_message(
                "Use b!ballout instead (i'm too lazy to implement this one)",
                ephemeral=True
            )
            return

        pt = pytz.timezone('America/Vancouver')
        weekday = datetime.now(pt).weekday()

        if weekday != 4:
            await ctx.reply("It's not Friday in Pacific Time yet...")
            return

        if ctx.channel.id != GFG_NSFW_ID:
            await ctx.reply(f'<#{GFG_NSFW_ID}>')
            return

        await ctx.channel.send(file=discord.File('assets/ballout.png'))


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
