import os
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_TEST_SERVER = int(os.getenv('BOT_TEST_SERVER_ID'))

OSU_CLIENT_ID = int(os.getenv('OSU_CLIENT_ID'))
OSU_CLIENT_SECRET = os.getenv('OSU_CLIENT_SECRET')

GFG_SERVER = int(os.getenv('GFG_SERVER_ID'))
GFG_GENERAL_ID = int(os.getenv('GFG_GENERAL_ID'))
GFG_NSFW_ID = int(os.getenv('GFG_NSFW_ID'))
GFG_LOGS_ID = int(os.getenv('GFG_LOGS_ID'))
GFG_GOLDFISH_EMOTE = os.getenv('GFG_GOLDFISH_EMOTE')

MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PW = os.getenv('MYSQL_PW')
OSUGFG_DB_NAME = os.getenv('OSUGFG_DB_NAME')
