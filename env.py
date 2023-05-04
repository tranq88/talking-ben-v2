import os
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_TEST_SERVER = int(os.getenv('BOT_TEST_SERVER_ID'))
GFG_SERVER = int(os.getenv('GFG_SERVER_ID'))
GFG_GENERAL_ID = int(os.getenv('GFG_GENERAL_ID'))
