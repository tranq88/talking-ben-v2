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


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
