# Most of the code in this file is from
# https://github.com/Varkaria/guweb/blob/37a18cd29fd1e5ede4fd8396645933df7f3510e0/blueprints/frontend.py#L447-L560

import discord
from discord import ui

from env import MYSQL_USERNAME, MYSQL_PW, OSUGFG_DB_NAME
from jsons import read_json, write_json

import re
import hashlib
import bcrypt
import aiomysql


username_re = re.compile(r'^[\w \[\]-]{2,15}$')
email_re = re.compile(r'^[^@\s]{1,200}@[^@\s\.]{1,30}\.[^@\.\s]{1,24}$')


def get_safe_name(name: str) -> str:
    """
    Return the safe version of a username.

    A safe name is a fully lowercase username with
    all spaces replaced by underscores.
    """
    return name.lower().replace(' ', '_')


async def register_db(name: str,
                      safe_name: str,
                      email: str,
                      pw_plaintext: str,
                      country: str):
    """Register a new account in the osu!Goldfish database."""
    # hash password (plaintext -> md5 -> bcrypt)
    pw_md5 = hashlib.md5(pw_plaintext.encode()).hexdigest().encode()
    pw_bcrypt = bcrypt.hashpw(pw_md5, bcrypt.gensalt())

    # insert into db
    async with aiomysql.connect(
        host='localhost',
        user=MYSQL_USERNAME,
        password=MYSQL_PW,
        db=OSUGFG_DB_NAME
    ) as conn:
        async with conn.cursor() as cur:
            # add to `users` table.
            await cur.execute(
                'INSERT INTO users '
                '(name, safe_name, email, pw_bcrypt, country, '
                'creation_time, latest_activity) '

                'VALUES '
                '(%s, %s, %s, %s, %s, UNIX_TIMESTAMP(), UNIX_TIMESTAMP())',
                [name, safe_name, email, pw_bcrypt, country]
            )
            user_id = cur.lastrowid

            # add to `stats` table.
            await cur.executemany(
                'INSERT INTO stats '
                '(id, mode) VALUES (%s, %s)',
                [(user_id, mode) for mode in (
                    0,  # vn!std
                    1,  # vn!taiko
                    2,  # vn!catch
                    3,  # vn!mania
                    4,  # rx!std
                    5,  # rx!taiko
                    6,  # rx!catch
                    8,  # ap!std
                )]
            )

            await conn.commit()


class AccountRegistration(ui.Modal, title='osu!Goldfish Account Registration'):
    """osu! private server account registration form."""
    username = ui.TextInput(
        label='Username',
        placeholder='tranq',
        min_length=2,
        max_length=15
    )
    email = ui.TextInput(label='Email Address', placeholder='hi@example.com')
    pw_plaintext = ui.TextInput(
        label='Password',
        placeholder='This form is not fully secure; choose a unique password.',
        min_length=8,
        max_length=32
    )

    async def on_submit(self, interaction: discord.Interaction):
        server_accs = read_json('server_accs.json')
        errors = []  # respond to the user any errors their form submission has

        # validate username
        if not username_re.match(str(self.username)):
            errors.append('Invalid username syntax.')

        if '_' in str(self.username) and ' ' in str(self.username):
            errors.append('Username may contain "_" or " ", but not both.')

        if get_safe_name(str(self.username)) in server_accs:
            errors.append('Username already taken by another user.')

        # validate email
        if not email_re.match(str(self.email)):
            errors.append('Invalid email syntax.')

        for acc in server_accs:
            if server_accs[acc]['email'] == str(self.email):
                errors.append('Email already taken by another user.')
                break

        # validate password
        if len(set(str(self.pw_plaintext))) <= 3:
            errors.append('Password must have more than 3 unique characters.')

        if errors:
            await interaction.response.send_message(
                (
                    '**Account registration was unsuccessful due to the '
                    'following error(s):**\n{}'.format('\n'.join(errors))
                ),
                ephemeral=True
            )
            return

        await register_db(
            str(self.username),
            get_safe_name(str(self.username)),
            str(self.email),
            str(self.pw_plaintext),
            'ca'
        )

        server_accs[get_safe_name(str(self.username))] = {
            'discord_id': interaction.user.id,
            'email': str(self.email)
        }
        write_json('server_accs.json', server_accs)

        await interaction.response.send_message(
            f'You have successfully registered as **{self.username}** '
            'on the osu!Goldfish private server!'
        )
