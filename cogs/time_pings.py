import discord
from discord.ext import commands, tasks
from discord import app_commands

from config import read_config, write_config
from env import BOT_TEST_SERVER, GFG_SERVER, GFG_GENERAL_ID
import datetime
import pytz


class TimePings(commands.Cog):
    """Handle time pings."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.gfg_general = bot.get_channel(GFG_GENERAL_ID)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Begin scheduled pings at 7:27pm for
        Ontario, Alberta and British Columbia.
        """
        self.time_pm_on.start()
        self.time_pm_ab.start()
        self.time_pm_bc.start()

    @commands.hybrid_command(
        name='time',
        description='''Schedule daily pings to someone at 7:27pm.
         Use /mutetime to avoid being pinged.'''
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    @app_commands.describe(user='da user')
    async def time(self, ctx: commands.Context, user: discord.Member):
        config = read_config('config.json')
        await ctx.reply(user)

    # -----------------------------
    #           Ontario
    # -----------------------------
    @tasks.loop(hours=24)
    async def time_pm_on(self):
        config = read_config('config.json')
        await self.gfg_general.send(f'<@{config["time_pingee"]}> time')

    @time_pm_on.before_loop
    async def wait_until_727pm_on(self):
        now = datetime.datetime.now(pytz.timezone('America/Toronto'))
        next_run = now.replace(hour=19, minute=27, second=1)

        if next_run < now:
            next_run += datetime.timedelta(days=1)

        await discord.utils.sleep_until(next_run)

    # -----------------------------
    #           Alberta
    # -----------------------------
    @tasks.loop(hours=24)
    async def time_pm_ab(self):
        config = read_config('config.json')
        await self.gfg_general.send(f'<@{config["time_pingee"]}> alberta time')

    @time_pm_ab.before_loop
    async def wait_until_727pm_ab(self):
        now = datetime.datetime.now(pytz.timezone('America/Edmonton'))
        next_run = now.replace(hour=19, minute=27, second=1)

        if next_run < now:
            next_run += datetime.timedelta(days=1)

        await discord.utils.sleep_until(next_run)

    # -----------------------------
    #       British Columbia
    # -----------------------------
    @tasks.loop(hours=24)
    async def time_pm_bc(self):
        config = read_config('config.json')
        await self.gfg_general.send(f'<@{config["time_pingee"]}> bc time')

    @time_pm_bc.before_loop
    async def wait_until_727pm_bc(self):
        now = datetime.datetime.now(pytz.timezone('America/Vancouver'))
        next_run = now.replace(hour=19, minute=27, second=1)

        if next_run < now:
            next_run += datetime.timedelta(days=1)

        await discord.utils.sleep_until(next_run)


async def setup(bot: commands.Bot):
    await bot.add_cog(TimePings(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
