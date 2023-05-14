import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

import os
from jsons import read_json, write_json
from env import BOT_TEST_SERVER, GFG_SERVER, GFG_GOLDFISH_EMOTE
from typing import Optional

from paginator import Paginator, PaginatorButtons


class Autism(commands.Cog):
    """Handle the autism test score leaderboard."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name='autismlb',
        description='View the autism test score leaderboard.'
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def autismlb(self, ctx: commands.Context):
        lb = read_json('autismlb.json')

        # sort by score in descending order
        descending_lb = sorted(
            lb.items(),
            key=lambda x: int(x[0]),
            reverse=True
        )

        # unpack each user from <score:users> into its own pair
        unpacked = []
        for pair in descending_lb:
            score = pair[0]
            for user_id in pair[1]:
                user = self.bot.get_user(user_id)
                if not user:
                    continue

                unpacked.append((
                    score,
                    str(user)[:-5]  # username without discriminator
                ))

        lines = [
            '{:6s}{:7s}{}'.format(
                f'[#{str(i + 1)}]',
                pair[0].center(5),
                pair[1]
            )
            for i, pair in enumerate(unpacked)
        ]

        title = f'{GFG_GOLDFISH_EMOTE} GOLDFISH GANG 😈 AUTISM 🙀 RANKINGS 🏅'
        p = Paginator(
            title=title,
            url=ctx.guild.icon.url,
            elements=lines,
            max_per_page=10,
            extra_footer=f' | Ranked Members: {len(lines)}',
            formatter='```',
            body_header='{:6s}{:7s}{}\n'.format('Rank', 'Score', 'Username')
        )

        if len(p) == 1:  # send without buttons
            await ctx.reply(
                embed=p.current_page(),
                mention_author=False
            )
        else:
            view = PaginatorButtons(p)
            view.message = await ctx.reply(
                embed=p.current_page(),
                view=view,
                mention_author=False
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Autism(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
