from typing import Optional

from env import VM_OSU_CACHE_DIR, MYSQL_USERNAME, MYSQL_PW, OSUGFG_DB_NAME
from jsons import read_json, write_json

from utils.gfg_api import Score, get_player_info, get_player_scores
from utils.gfg_server_accs import find_user
from utils.account_registration import get_safe_name, username_re
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
from rosu_pp_py import Beatmap, Calculator
import aiomysql

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


def calc_star_rating(mode: int, score: Score) -> float:
    """
    Calculate the star rating of the map associated with <score>
    with <score>'s mods applied.
    """
    try:
        map = Beatmap(path=f'{VM_OSU_CACHE_DIR}/{score.beatmap.diff_id}.osu')
    except Exception:  # should be a ParseError when testing locally
        # can't catch directly because the error is defined in Rust :(
        return score.beatmap.star_rating

    calc = Calculator(
        mode=(0 if mode == 4 else mode),  # treat relax as standard
        mods=score.mods.value
    )
    return calc.difficulty(map).stars


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
                f'[{calc_star_rating(mode, score):.2f}★]'
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


async def process_best_scores(ctx: Context,
                              username: Optional[str],
                              mode: int) -> None:
    """Get an osu!Goldfish user's top plays."""
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

    user_scores = get_player_scores(
        name=user.name,
        mode=mode,
        scope='best',
        limit=100
    )
    if not user_scores:
        await ctx.reply(
            content=(
                f'``{user.name}`` has no {modes[mode]} plays '
                'on osu!Goldfish.'
            ),
            mention_author=False
        )
        return

    # partition into groups of 5 (so we can show 5 scores per page)
    partitions = [user_scores[i:i+5] for i in range(0, len(user_scores), 5)]
    pages: list[discord.Embed] = []

    idx = 1
    for partition in partitions:
        description = ''
        for score in partition:
            description += (
                f'**{idx}) '
                f'[{score.beatmap.title} [{score.beatmap.difficulty}]]'
                f'(https://osu.ppy.sh/b/{score.beatmap.diff_id}) '
                f'+{score.mods.short_name()}** '
                f'[{calc_star_rating(mode, score):.2f}★]\n'

                f'▸ {get_grade_emoji(score.grade)} ▸ **{score.pp:.2f}pp** '
                f'▸ {score.acc:.2f}%\n'

                f'▸ {score.score:,} '
                f'▸ x{score.max_combo}/{score.beatmap.max_combo} '
                f'▸ [{score.n300}/{score.n100}/{score.n50}/{score.nmiss}]\n'

                f'▸ Score set <t:{int(score.play_time.timestamp())}:R>\n'
            )
            idx += 1

        em = discord.Embed(
            description=description,
            colour=discord.Colour.from_rgb(181, 142, 101)
        )
        em.set_author(
            name=f'Top {modes[mode]} Plays for {user.name}',
            url=f'https://osu.victoryu.dev/u/{user.id}',
            icon_url=(
                f'https://assets.ppy.sh/old-flags/{user.country.upper()}.png'
            )
        )
        em.set_thumbnail(url=f'https://a.victoryu.dev/{user.id}')
        em.set_footer(text='On osu!Goldfish server')

        pages.append(em)

    await reply_paginator(
        paginator=Paginator(pages=pages),
        ctx=ctx
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


async def process_name_change(ctx: Context,
                              new_name: str) -> None:
    """Change a user's name on osu!Goldfish."""
    server_accs = read_json('server_accs.json')

    try:
        safe_old_name = find_user(server_accs, ctx.author.id)
    except LookupError:
        await ctx.reply('You are not registered on osu!Goldfish.')
        return

    if not username_re.match(new_name):
        await ctx.reply('Invalid username syntax.')
        return

    if '_' in new_name and ' ' in new_name:
        await ctx.reply('Username may contain "_" or " ", but not both.')
        return

    safe_new_name = get_safe_name(new_name)

    if safe_new_name in server_accs:
        await ctx.reply('Username already taken by another user.')
        return

    # update the database
    async with aiomysql.connect(
        host='localhost',
        user=MYSQL_USERNAME,
        password=MYSQL_PW,
        db=OSUGFG_DB_NAME
    ) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                'UPDATE users '
                'SET name = %s, safe_name = %s '
                'WHERE safe_name = %s',
                [new_name, safe_new_name, safe_old_name]
            )
            await conn.commit()

    # replace the old name with safe_new_name in the json
    server_accs[safe_new_name] = server_accs.pop(safe_old_name)
    write_json('server_accs.json', server_accs)

    await ctx.reply(
        f'Your osu!Goldfish username has been changed to **{new_name}**!'
    )
