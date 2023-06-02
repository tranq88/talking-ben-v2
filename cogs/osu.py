import discord
from discord.ext import commands
from discord import app_commands

from env import BOT_TEST_SERVER, GFG_SERVER, OSU_CLIENT_ID, OSU_CLIENT_SECRET
from jsons import read_json

from paginator import Paginator, PaginatorButtons
from account_registration import AccountRegistration
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

    @app_commands.command(
        name='register',
        description=('Register an account on the '
                     'Goldfish Gang osu! private server.')
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def register(self, interaction: discord.Interaction):
        server_accs = read_json('server_accs.json')

        for acc in server_accs:
            if server_accs[acc]['discord_id'] == interaction.user.id:
                await interaction.response.send_message(
                    f'You are registered on osu!Goldfish as **{acc}**.',
                    ephemeral=True
                )
                return

        await interaction.response.send_modal(AccountRegistration())

    @commands.hybrid_command(
        name='privserver',
        description=('View instructions on how to play on the '
                     'Goldfish Gang osu! private server.')
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def privserver(self, ctx: commands.Context):
        await ctx.reply(
            '**How to play on osu!Goldfish:**\n\n'

            '**1.** Register for an account with ``/register``.\n'
            '**2.** Create a copy of your osu! shortcut.\n'
            '**3.** Right click your new shortcut and click ``Properties``.\n'
            '**4.** In ``Target``, add ``-devserver victoryu.dev`` to the '
            'end of the path so that it looks something like '
            '``C:\\...\\osu!\\osu!.exe -devserver victoryu.dev``.\n'
            '**5.** Log in with your credentials and play!\n\n'

            '**Note: This server is new so expect things to be scuffed.**',
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Osu(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
