import discord

from env import MYSQL_USERNAME, MYSQL_PW, OSUGFG_DB_NAME

import aiomysql
from iso3166 import countries


async def update_flag_in_db(user_safe_name: str,
                            country_code: str):
    """Update a user's flag in the osu!Goldfish database."""
    country_code = country_code.lower()

    async with aiomysql.connect(
        host='localhost',
        user=MYSQL_USERNAME,
        password=MYSQL_PW,
        db=OSUGFG_DB_NAME
    ) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                'UPDATE users SET country = %s WHERE safe_name = %s',
                [country_code, user_safe_name]
            )
            await conn.commit()


async def process_flag_change(interaction: discord.Interaction,
                              user_safe_name: str,
                              country_code: str):
    """Change a user's flag on osu!Goldfish."""
    country_code = country_code.lower()

    # validate the country code
    try:
        countries.get(country_code)
    except KeyError:
        await interaction.response.send_message(
            'Invalid country code. Refer to the Alpha-2 column at '
            'https://www.iban.com/country-codes for a list of country codes.',
            ephemeral=True
        )
        return
    
    await update_flag_in_db(user_safe_name, country_code)
    await interaction.response.send_message(
        f'Flag successfully changed to :flag_{country_code}:.'
    )
