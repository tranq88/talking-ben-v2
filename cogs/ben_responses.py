import discord
from discord.ext import commands
from discord import app_commands

import os
import random
from config import read_config, write_config


class BenResponses(commands.Cog):
    """Talking Ben responses."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.content.endswith('?'):
            return

        config = read_config('config.json')

        if message.channel in config['response_channels']:
            responses = [discord.File(f'./assets/ben_responses/{filename}')
                         for filename in os.listdir('./assets/ben_responses')]
            await message.reply(file=random.choice(responses))

    @commands.hybrid_command(
        name='toggleresponses',
        description='Toggle Talking Ben responses for this channel.'
    )
    @app_commands.guilds(discord.Object(id=952066732120473630))
    async def toggleresponses(self, ctx: commands.Context):
        await ctx.reply('Hi')


async def setup(bot: commands.Bot):
    await bot.add_cog(BenResponses(bot),
                      # bot test server id
                      guild=discord.Object(id=952066732120473630))
