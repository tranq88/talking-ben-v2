import discord
from discord.ext import commands
import asyncio

import os
from dotenv import load_dotenv


class Bot(commands.Bot):
    def __init__(self) -> None:

        intents = discord.Intents.default()
        super().__init__(command_prefix='b!', intents=intents)

        asyncio.run(self.load_cogs())

        self.synced = False

    async def load_cogs(self) -> None:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

    async def on_ready(self) -> None:
        await self.wait_until_ready()

        if not self.synced:
            await self.tree.sync(
                guild=discord.Object(id=952066732120473630))  # bts id
            self.synced = True

        print(f'Logged in as {self.user}')


if __name__ == '__main__':

    load_dotenv()

    bot = Bot()
    bot.run(os.getenv('BOT_TOKEN'))
