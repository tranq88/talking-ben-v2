import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

import os
from jsons import read_json, write_json
from env import BOT_TEST_SERVER, GFG_SERVER
from typing import Optional

from paginator import Paginator, PaginatorButtons


class Tags(commands.Cog):
    """Handle tags."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """View a tag."""
        if not (message.content.startswith('b!') and
                message.author != self.bot.user):
            return

        tags = read_json('tags.json')
        check = message.content.split('b!', 1)[1]

        if check in tags:
            if 'message' in tags[check]:
                await message.channel.send(tags[check]['message'])
            else:  # it's an attachment tag
                filename = tags[check]['filename']
                file = discord.File(f'./assets/tags/{filename}')
                await message.channel.send(file=file)

    @commands.hybrid_group(name='tag', aliases=['t'])
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def tag(self, ctx: commands.Context):
        await ctx.reply(
            ('To view a tag, do ``b!(tag name)``. '
             "Do ``/tag list`` to view this server's tags.")
        )

    @tag.command(
        name='add',
        description=('Create a tag of either a message '
                     'or an attachment.')
    )
    @commands.has_permissions(administrator=True)
    @app_commands.describe(attachment=('Providing an attachment will ignore '
                                       'any argument for [message].'))
    async def add(self,
                  ctx: commands.Context,
                  tag_name: str,
                  message: Optional[str],
                  attachment: Optional[discord.Attachment]):
        if not ctx.interaction:
            await ctx.reply("Use ``/tag add`` instead, it's just better 😄")
            return

        if not (message or attachment):
            await ctx.interaction.response.send_message(
                'You must provide either a ``message`` or an ``attachment``.',
                ephemeral=True
            )
            return

        tags = read_json('tags.json')

        if tag_name in tags:
            await ctx.interaction.response.send_message(
                'That tag already exists!',
                ephemeral=True
            )
            return
        elif tag_name in [command.name for command in self.bot.commands]:
            await ctx.interaction.response.send_message(
                'A command with this name already exists!',
                ephemeral=True
            )
            return

        if attachment:
            file_extension = attachment.filename.rsplit('.', 1)[1]
            new_filename = tag_name + '.' + file_extension

            tags[tag_name] = {'filename': new_filename}
            await attachment.save(f'./assets/tags/{new_filename}')
        else:
            tags[tag_name] = {'message': message}

        write_json('tags.json', tags)
        await ctx.interaction.response.send_message(
            f'Successfully tagged as ``{tag_name}``.'
        )

    @tag.command(
        name='delete',
        aliases=['del'],
        description='Delete a tag.'
    )
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx: commands.Context, tag_name: str):
        tags = read_json('tags.json')

        if tag_name not in tags:
            await ctx.reply('That tag does not exist!')
            return

        if 'filename' in tags[tag_name]:
            os.remove(f"./assets/tags/{tags[tag_name]['filename']}")

        tags.pop(tag_name)
        write_json('tags.json', tags)

        await ctx.reply(f'Deleted tag ``{tag_name}``.')

    @tag.command(name='list', description="View this server's tags.")
    @app_commands.describe(sort='Default sort: Date added (newest first)')
    @app_commands.choices(sort=[
        Choice(name='Alphabetical', value=1),
        Choice(name='Date added (oldest first)', value=2)
    ])
    async def list(self, ctx: commands.Context, sort: Choice[int] = None):
        tags = read_json('tags.json')

        if not sort:  # default sort
            tags = dict(list(tags.items())[::-1])
            sort_type = 'Date added (newest first)'
        elif sort.value == 1:
            tags = dict(sorted(tags.items()))
            sort_type = sort.name
        else:
            # <tags> is already sorted by oldest first
            sort_type = sort.name

        p = Paginator(
            title='Tags for Goldfish Gang',
            thumbnail_url=ctx.guild.icon.url,
            elements=['b!' + tag for tag in tags],
            max_per_page=10,
            extra_footer=f' | Sort: {sort_type}'
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
    await bot.add_cog(Tags(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
