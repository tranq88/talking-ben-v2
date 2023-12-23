# Most of the code in this file is from
# https://github.com/Varkaria/guweb/blob/37a18cd29fd1e5ede4fd8396645933df7f3510e0/blueprints/frontend.py#L447-L560

import discord
from discord import ui

from env import MYSQL_USERNAME, MYSQL_PW, OSUGFG_DB_NAME
from utils.account_registration import hash_password

import aiomysql


async def update_pw_in_db(user_safe_name: str,
                          pw_plaintext: str):
    """Update a user's password in the osu!Goldfish database."""
    hashed_pw = hash_password(pw_plaintext)

    async with aiomysql.connect(
        host='localhost',
        user=MYSQL_USERNAME,
        password=MYSQL_PW,
        db=OSUGFG_DB_NAME
    ) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                'UPDATE users SET pw_bcrypt = %s WHERE safe_name = %s',
                [hashed_pw, user_safe_name]
            )
            await conn.commit()


class PasswordChanger(ui.Modal, title='osu!Goldfish Password Change'):
    """osu! private server password change form."""
    def __init__(self, user_safe_name: str):
        super().__init__()
        self.user_safe_name = user_safe_name

    pw_plaintext = ui.TextInput(
        label='New Password',
        placeholder='This form is not fully secure; choose a unique password.',
        min_length=8,
        max_length=32
    )

    async def on_submit(self, interaction: discord.Interaction):
        # validate password
        if len(set(str(self.pw_plaintext))) <= 3:
            await interaction.response.send_message(
                'Password must have more than 3 unique characters.',
                ephemeral=True
            )
            return

        await update_pw_in_db(
            self.user_safe_name,
            str(self.pw_plaintext)
        )
        await interaction.response.send_message(
            'Password successfully changed.'
        )
