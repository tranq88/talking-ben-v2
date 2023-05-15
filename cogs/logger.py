import discord
from discord.ext import commands

from env import BOT_TEST_SERVER, GFG_SERVER, GFG_LOGS_ID


class Logger(commands.Cog):
    """it's the opps"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, m: discord.Message):
        em = discord.Embed(
            description=(
                f"**Message sent by** <@{m.author.id}> "
                f"**deleted in** <#{m.channel.id}>\n{m.content}"
            ),
            colour=discord.Colour.from_rgb(240, 60, 50),
            timestamp=discord.utils.utcnow()
        )
        em.set_author(name=m.author, icon_url=m.author.avatar.url)

        await self.bot.get_channel(GFG_LOGS_ID).send(embed=em)


async def setup(bot: commands.Bot):
    await bot.add_cog(Logger(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
