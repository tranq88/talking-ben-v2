import discord
from discord.ext import commands
from discord import app_commands

from jsons import read_json, write_json
from env import BOT_TEST_SERVER, GFG_SERVER, GFG_GOLDFISH_EMOTE

from paginator import Paginator, PaginatorButtons
from member_conv import MemberConv


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
            thumbnail_url=ctx.guild.icon.url,
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
            view = PaginatorButtons(p, ctx.author)
            view.message = await ctx.reply(
                embed=p.current_page(),
                view=view,
                mention_author=False
            )

    @commands.hybrid_command(
        name='autismadd',
        description=(
            'Add a user to the autism leaderboard rankings; '
            "update a user's score if they're already ranked."
        )
    )
    @commands.has_permissions(administrator=True)
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def autismadd(self,
                        ctx: commands.Context,
                        user: app_commands.Transform[
                            discord.Member,
                            MemberConv
                        ],
                        score: str):
        if not user:
            await ctx.reply('User not found.')
            return

        lb = read_json('autismlb.json')

        # check if <user> is already ranked
        is_update = False
        for key in lb:
            if user.id in lb[key]:
                is_update = True
                lb[key].remove(user.id)
                break

        lb[score] = lb.get(score, []) + [user.id]
        write_json('autismlb.json', lb)

        if is_update:
            await ctx.reply(f'Updated ``{str(user)}`` to a score of '
                            f'``{score}`` in the rankings.')
        else:
            await ctx.reply(f'Added ``{str(user)}`` with a score of '
                            f'``{score}`` to the rankings.')

    @commands.hybrid_command(
        name='autismdel',
        description='Delete a user from the autism leaderboard rankings.'
    )
    @commands.has_permissions(administrator=True)
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def autismdel(self,
                        ctx: commands.Context,
                        user: app_commands.Transform[
                            discord.Member,
                            MemberConv
                        ]):
        if not user:
            await ctx.reply('User not found.')
            return

        lb = read_json('autismlb.json')
        for key in lb:
            if user.id in lb[key]:
                lb[key].remove(user.id)
                write_json('autismlb.json', lb)

                await ctx.reply(f'Removed ``{str(user)}`` from the rankings.')
                return

        await ctx.reply('User is not on the rankings.')


async def setup(bot: commands.Bot):
    await bot.add_cog(Autism(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
