import discord
from discord.ext import commands

from env import BOT_TEST_SERVER, GFG_SERVER, OSU_CLIENT_ID, OSU_CLIENT_SECRET

from ossapi import OssapiAsync


class Osu(commands.Cog):
    """osu!."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _osu_api(self) -> OssapiAsync:
        """
        Access the osu! API via client credentials and return
        the corresponding OssapiAsync object.
        """
        return OssapiAsync(OSU_CLIENT_ID, OSU_CLIENT_SECRET)


async def setup(bot: commands.Bot):
    await bot.add_cog(Osu(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
