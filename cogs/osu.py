import discord
from discord.ext import commands
from discord import app_commands

from typing import Optional
from env import BOT_TEST_SERVER, GFG_SERVER, OSU_CLIENT_ID, OSU_CLIENT_SECRET
from jsons import read_json

from utils.paginator import Paginator, reply_paginator
from utils.account_registration import AccountRegistration
from utils.osu_utils import (
    process_recent_scores,
    process_profile,
    process_best_scores
)
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

            '**1.** Register for an account with '
            '</register:1114101782545715321>.\n'
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
        description=(
            "Get a user's most recent osu! Standard play(s) on osu!Goldfish."
        )
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def recent(self,
                     ctx: commands.Context,
                     username: Optional[str] = None):
        await ctx.defer()
        await process_recent_scores(ctx=ctx, username=username, mode=0)

    @commands.hybrid_command(
        name='recenttaiko',
        aliases=['rstaiko'],
        description=(
            "Get a user's most recent osu! Taiko play(s) on osu!Goldfish."
        )
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def recenttaiko(self,
                          ctx: commands.Context,
                          username: Optional[str] = None):
        await ctx.defer()
        await process_recent_scores(ctx=ctx, username=username, mode=1)

    @commands.hybrid_command(
        name='recentcatch',
        aliases=['rscatch'],
        description=(
            "Get a user's most recent osu! Catch play(s) on osu!Goldfish."
        )
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def recentcatch(self,
                          ctx: commands.Context,
                          username: Optional[str] = None):
        await ctx.defer()
        await process_recent_scores(ctx=ctx, username=username, mode=2)

    @commands.hybrid_command(
        name='recentmania',
        aliases=['rsmania'],
        description=(
            "Get a user's most recent osu! Mania play(s) on osu!Goldfish."
        )
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def recentmania(self,
                          ctx: commands.Context,
                          username: Optional[str] = None):
        await ctx.defer()
        await process_recent_scores(ctx=ctx, username=username, mode=3)

    @commands.hybrid_command(
        name='recentrelax',
        aliases=['rsrelax'],
        description=(
            "Get a user's most recent osu! Relax play(s) on osu!Goldfish."
        )
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def recentrelax(self,
                          ctx: commands.Context,
                          username: Optional[str] = None):
        await ctx.defer()
        await process_recent_scores(ctx=ctx, username=username, mode=4)

    @commands.hybrid_command(
        name='osu',
        description=("View a user's osu! Standard profile on osu!Goldfish.")
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def osu(self,
                  ctx: commands.Context,
                  username: Optional[str] = None):
        await ctx.defer()
        await process_profile(ctx=ctx, username=username, mode=0)

    @commands.hybrid_command(
        name='taiko',
        description=("View a user's osu! Taiko profile on osu!Goldfish.")
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def taiko(self,
                    ctx: commands.Context,
                    username: Optional[str] = None):
        await ctx.defer()
        await process_profile(ctx=ctx, username=username, mode=1)

    @commands.hybrid_command(
        name='ctb',
        description=("View a user's osu! Catch profile on osu!Goldfish.")
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def ctb(self,
                  ctx: commands.Context,
                  username: Optional[str] = None):
        await ctx.defer()
        await process_profile(ctx=ctx, username=username, mode=2)

    @commands.hybrid_command(
        name='mania',
        description=("View a user's osu! Mania profile on osu!Goldfish.")
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def mania(self,
                    ctx: commands.Context,
                    username: Optional[str] = None):
        await ctx.defer()
        await process_profile(ctx=ctx, username=username, mode=3)

    @commands.hybrid_command(
        name='relax',
        aliases=['rx'],
        description=("View a user's osu! Relax profile on osu!Goldfish.")
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def relax(self,
                    ctx: commands.Context,
                    username: Optional[str] = None):
        await ctx.defer()
        await process_profile(ctx=ctx, username=username, mode=4)

    @commands.hybrid_command(
        name='osutop',
        description=("View a user's top osu! Standard plays on osu!Goldfish.")
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def osutop(self,
                     ctx: commands.Context,
                     username: Optional[str] = None):
        await ctx.defer()
        await process_best_scores(ctx=ctx, username=username, mode=0)

    @commands.hybrid_command(
        name='taikotop',
        description=("View a user's top osu! Taiko plays on osu!Goldfish.")
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def taikotop(self,
                       ctx: commands.Context,
                       username: Optional[str] = None):
        await ctx.defer()
        await process_best_scores(ctx=ctx, username=username, mode=1)

    @commands.hybrid_command(
        name='ctbtop',
        description=("View a user's top osu! Catch plays on osu!Goldfish.")
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def ctbtop(self,
                     ctx: commands.Context,
                     username: Optional[str] = None):
        await ctx.defer()
        await process_best_scores(ctx=ctx, username=username, mode=2)

    @commands.hybrid_command(
        name='maniatop',
        description=("View a user's top osu! Mania plays on osu!Goldfish.")
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def maniatop(self,
                       ctx: commands.Context,
                       username: Optional[str] = None):
        await ctx.defer()
        await process_best_scores(ctx=ctx, username=username, mode=3)

    @commands.hybrid_command(
        name='relaxtop',
        description=("View a user's top osu! Relax plays on osu!Goldfish.")
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def relaxtop(self,
                       ctx: commands.Context,
                       username: Optional[str] = None):
        await ctx.defer()
        await process_best_scores(ctx=ctx, username=username, mode=4)


async def setup(bot: commands.Bot):
    await bot.add_cog(Osu(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
