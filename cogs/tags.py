import discord
from discord.ext import commands, tasks
from discord import app_commands

from jsons import read_json, write_json
from env import BOT_TEST_SERVER, GFG_SERVER, GFG_GENERAL_ID
from member_conv import MemberConv
from typing import Optional


class Tags(commands.Cog):
    """Handle tags."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not (message.content.startswith('b!') and
                message.author != self.bot.user):
            return

        tags = read_json('tags.json')
        check = message.content.split('b!', 1)[1]

        if check in tags:
            if 'message' in tags[check]:
                await message.channel.send(tags[check]['message'])
            else:
                filename = tags[check]['filename']
                file = discord.File(f'./assets/tags/{filename}')
                await message.channel.send(file=file)

    @commands.hybrid_group(name='tag', aliases=['t'])
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def tag(self, ctx: commands.Context):
        await ctx.reply('tag')

    @tag.command(name='add')
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

    @tag.command(name='delete', aliases=['del'])
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx: commands.Context):
        await ctx.reply('tag delete')

    @tag.command(name='list')
    async def list(self, ctx: commands.Context):
        await ctx.reply('tag list')


async def setup(bot: commands.Bot):
    await bot.add_cog(Tags(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
