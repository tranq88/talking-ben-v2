import discord
from discord.ext import commands
from discord import app_commands

from env import BOT_TEST_SERVER, GFG_SERVER, OSU_CLIENT_ID, OSU_CLIENT_SECRET

from paginator import Paginator, PaginatorButtons
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

    @commands.hybrid_command(
        name='recentbadge',
        aliases=['rbadge'],
        description="View an osu! user's most recent badge(s)."
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def recentbadge(self, ctx: commands.Context, *, username: str):
        await ctx.defer()

        try:
            user = await self._osu_api().user(username)
        except ValueError:
            await ctx.reply('User not found.')
            return

        if not user.badges:
            await ctx.reply('User has no badges 💀')
            return

        p = Paginator(
            author={
                'name': (
                    f'{user.username}: {user.statistics.pp:,}pp '
                    f'(#{user.statistics.global_rank:,} '
                    f'{user.country_code}{user.statistics.country_rank})'
                ),
                'url': f'https://osu.ppy.sh/users/{user.id}',
                'icon_url': (
                    f'https://assets.ppy.sh/old-flags/{user.country_code}.png'
                )
            },
            thumbnail_url=f'http://s.ppy.sh/a/{user.id}',
            title=f'Most recently awarded badge(s) for {user.username}',
            elements=[badge.description for badge in user.badges],
            max_per_page=1,
            image_urls=[badge.image_url for badge in user.badges],
            timestamps=[badge.awarded_at for badge in user.badges]
        )

        if len(p) == 1:  # send without buttons
            await ctx.reply(
                embed=p.current_page(),
                mention_author=False
            )
        else:
            view = PaginatorButtons(p, ctx.author)
            view.message = await ctx.reply(
                embed=p.current_page(),
                view=view,
                mention_author=False
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Osu(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
