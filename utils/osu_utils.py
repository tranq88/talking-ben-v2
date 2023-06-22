from typing import Optional

from jsons import read_json
from utils.gfg_api import Score, get_player_info, get_player_scores
from utils.gfg_server_accs import find_user
from utils.account_registration import get_safe_name
from utils.paginator import Paginator, reply_paginator
from utils.emojis import (
    RANKING_SSH,
    RANKING_SS,
    RANKING_SH,
    RANKING_S,
    RANKING_A,
    RANKING_B,
    RANKING_C,
    RANKING_D,
    RANKING_F
)

import discord
from discord.ext.commands import Context
from requests.exceptions import HTTPError


modes = [  # convenient mode indexing for functions that need it
    'osu! Standard',     # 0
    'osu! Taiko',        # 1
    'osu! Catch',        # 2
    'osu! Mania',        # 3
    'osu! Relax',        # 4
    'osu! Relax Taiko',  # 5
    'osu! Relax Catch',  # 6
    None,                # placeholder
    'osu! Autopilot'     # 8
]


def get_grade_emoji(grade: str) -> Optional[str]:
    """Return the corresponding emoji for the given osu! score grade."""
    if grade == 'XH':
        return RANKING_SSH
    elif grade == 'X':
        return RANKING_SS
    elif grade == 'SH':
        return RANKING_SH
    elif grade == 'S':
        return RANKING_S
    elif grade == 'A':
        return RANKING_A
    elif grade == 'B':
        return RANKING_B
    elif grade == 'C':
        return RANKING_C
    elif grade == 'D':
        return RANKING_D
    elif grade == 'F':
        return RANKING_F


def calc_map_completion(score: Score) -> float:
    """Calculate the percentage of map completed as given by <score>."""
    return score.time_elapsed / 1000 / score.beatmap.length * 100


async def process_recent_scores(ctx: Context,
                                username: Optional[str],
                                mode: int) -> None:
    """Get an osu!Goldfish user's most recent scores."""
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

    user_scores = get_player_scores(name=user.name, mode=mode)
    if not user_scores:
        await ctx.reply(
            content=(
                f'``{user.name}`` has no recent {modes[mode]} plays '
                'on osu!Goldfish.'
            ),
            mention_author=False
        )
        return

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
        content=f'**Recent {modes[mode]} Play for {user.name}:**'
    )


async def process_profile(ctx: Context,
                          username: Optional[str],
                          mode: int) -> None:
    """Get an osu!Goldfish user's profile and statistics."""
    server_accs = read_json('server_accs.json')

    if not username:  # search for the user's account
        try:
            username = find_user(server_accs, ctx.author.id)
        except LookupError:
            await ctx.reply('You are not registered on osu!Goldfish.')
            return

    try:
        user = get_player_info(name=username, mode=mode)
    except HTTPError:
        await ctx.reply('User not found.')
        return

    em = discord.Embed(
        description=(
            f'▸ **Goldfish Rank:** #{user.stats.rank}\n'

            f'▸ **Discord:** '
            f'<@{server_accs[get_safe_name(user.name)]["discord_id"]}>\n'

            f'▸ **PP:** {int(user.stats.pp):,} '
            f'**Accuracy:** {float(user.stats.acc):.2f}%\n'

            f'▸ **Playcount:** {int(user.stats.playcount):,} '
            f'({int(user.stats.playtime) // 3600:,} hrs)\n'

            f'▸ **Replay Views:** {int(user.stats.replay_views):,}\n'

            f'▸ **Ranks:** {RANKING_SSH}``{int(user.stats.xh_count):,}``'
            f'{RANKING_SS}``{int(user.stats.x_count):,}``'
            f'{RANKING_SH}``{int(user.stats.sh_count):,}``'
            f'{RANKING_S}``{int(user.stats.s_count):,}``'
            f'{RANKING_A}``{int(user.stats.a_count):,}``'
        ),
        colour=discord.Colour.from_rgb(181, 142, 101)
    )

    em.set_author(
        name=f"{modes[mode]} Profile for {user.name}",
        url=f"https://osu.victoryu.dev/u/{user.id}",
        icon_url=(
            f"https://assets.ppy.sh/old-flags/{user.country.upper()}.png"
        )
    )
    em.set_thumbnail(url=f"https://a.victoryu.dev/{user.id}")
    em.set_footer(text="On osu!Goldfish server")

    await ctx.reply(embed=em, mention_author=False)
