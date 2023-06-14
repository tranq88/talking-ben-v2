import discord
from discord.ext import commands
from discord import app_commands

from typing import Optional
from env import BOT_TEST_SERVER, GFG_SERVER, OSU_CLIENT_ID, OSU_CLIENT_SECRET
from jsons import read_json

from utils.paginator import Paginator, reply_paginator
from utils.account_registration import AccountRegistration
from utils.gfg_api import (
    get_player_scores,
    get_player_info,
    get_grade_emoji,
    calc_map_completion
)
from utils.gfg_server_accs import find_user
from requests.exceptions import HTTPError
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

        pages: list[discord.Embed] = []

        for badge in user.badges:
            em = discord.Embed(
                title=f'Most recently awarded badge(s) for {user.username}',
                description=badge.description,
                timestamp=badge.awarded_at,
                colour=discord.Colour.from_rgb(181, 142, 101)
            )

            em.set_author(
                name=(
                    f'{user.username}: {user.statistics.pp:,}pp '
                    f'(#{user.statistics.global_rank:,} '
                    f'{user.country_code}{user.statistics.country_rank})'
                ),
                url=f'https://osu.ppy.sh/users/{user.id}',
                icon_url=(
                    f'https://assets.ppy.sh/old-flags/{user.country_code}.png'
                )
            )

            em.set_thumbnail(url=f'http://s.ppy.sh/a/{user.id}')
            em.set_image(url=badge.image_url)

            pages.append(em)

        await reply_paginator(paginator=Paginator(pages=pages), ctx=ctx)

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

    @commands.hybrid_command(
        name='recent',
        aliases=['rs'],
        description=("Get a user's most recent play(s) on osu!Goldfish.")
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def recent(self,
                     ctx: commands.Context,
                     username: Optional[str] = None):
        await ctx.defer()

        if not username:  # search for the user's account
            server_accs = read_json('server_accs.json')
            try:
                username = find_user(server_accs, ctx.author.id)
            except LookupError:
                await ctx.reply('You are not registered on osu!Goldfish.')
                return

        try:
            user = get_player_info(name=username)
        except HTTPError:
            await ctx.reply('User not found.')
            return

        user_scores = get_player_scores(name=user.name)
        pages: list[discord.Embed] = []

        for score in user_scores:
            completion = (
                f' ({calc_map_completion(score):.2f}%)' if score.grade == 'F'
                else ''
            )
            em = discord.Embed(
                description=(
                    f"▸ {get_grade_emoji(score.grade)}{completion} ▸ "
                    f"**{score.pp:.2f}pp** ▸ "
                    # f"({calc_fc_pp()}PP for {calc_fc_acc()}% FC) ▸ "
                    f"{score.acc:.2f}% ▸ "
                    f"<t:{int(score.play_time.timestamp())}:R>"
                    f"\n▸ {score.score:,} ▸ "
                    f"x{score.max_combo}/{score.beatmap.max_combo} ▸ "
                    f"[{score.n300}/{score.n100}/{score.n50}/{score.nmiss}]"
                ),
                timestamp=score.play_time,
                colour=discord.Colour.from_rgb(181, 142, 101)
            )

            em.set_author(
                name=(
                    f'{score.beatmap.title} [{score.beatmap.difficulty}] '
                    f'+{score.mods.short_name()} '
                    f'[{score.beatmap.star_rating:.2f}★]'
                ),
                url=f'https://osu.ppy.sh/b/{score.beatmap.diff_id}',
                icon_url=f'https://a.victoryu.dev/{user.id}'
            )

            em.set_thumbnail(
                url=f'https://b.ppy.sh/thumb/{score.beatmap.set_id}l.jpg'
            )

            footer = (
                "WYSI" if score.max_combo == 727 else "On osu!Goldfish server"
            )
            em.set_footer(text=footer)

            pages.append(em)

        await reply_paginator(
            paginator=Paginator(pages=pages, show_index=False),
            ctx=ctx,
            content=f'**Recent osu! Standard Play for {user.name}:**'
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Osu(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
