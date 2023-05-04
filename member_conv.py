import discord
from discord import app_commands
from discord.ext import commands


class MemberConv(commands.Converter, app_commands.Transformer):
    """Ease searching members in hybrid commands."""
    @property
    def type(self) -> discord.AppCommandOptionType.user:
        return discord.AppCommandOptionType.user

    # App command
    async def transform(self, interaction, value):
        return value

    # Chat command
    async def convert(self, ctx, argument):
        try:
            return await commands.MemberConverter().convert(ctx, argument)
        except commands.MemberNotFound:
            check = argument.lower()

            # Search username
            member = discord.utils.find(
                lambda m: m.name.lower().startswith(check), ctx.guild.members
            )

            if not member:
                # Search nickname
                member = discord.utils.find(
                    lambda m: m.display_name.lower().startswith(check),
                    ctx.guild.members
                )

            return member
