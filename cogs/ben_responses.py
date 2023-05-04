import discord
from discord.ext import commands
from discord import app_commands

import os
import random
from config import read_config, write_config
from env import BOT_TEST_SERVER, GFG_SERVER


class BenResponses(commands.Cog):
    """Talking Ben responses."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Respond to messages ending with a question mark if the channel
        has Ben responses enabled.
        """
        if not message.content.endswith('?'):
            return

        config = read_config('config.json')

        if message.channel.id in config['response_channels']:
            responses = [discord.File(f'./assets/ben_responses/{filename}')
                         for filename in os.listdir('./assets/ben_responses')]
            await message.reply(file=random.choice(responses))

    @commands.hybrid_command(
        name='toggleresponses',
        description='Toggle Talking Ben responses for this channel.'
    )
    @app_commands.guilds(BOT_TEST_SERVER, GFG_SERVER)
    async def toggleresponses(self, ctx: commands.Context):
        config = read_config('config.json')
        id_ = ctx.channel.id

        if id_ in config['response_channels']:
            config['response_channels'].remove(id_)
            await ctx.reply(f'Toggled off Ben responses for <#{id_}>')
        else:
            config['response_channels'].append(id_)
            await ctx.reply(f'Toggled on Ben responses for <#{id_}>')

        write_config('config.json', config)


async def setup(bot: commands.Bot):
    await bot.add_cog(BenResponses(bot),
                      guilds=[discord.Object(id=BOT_TEST_SERVER),
                              discord.Object(id=GFG_SERVER)])
