import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from database.database import Database
from events import setup_events
from commands.setup import setup_commands
from utils.utils import HelperUtils
from context import BotContext

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set.")
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN environment variable is not set.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
database = Database(MONGO_URI)
helper_utils = HelperUtils(client, database)

context = BotContext(database, helper_utils, client, tree)

setup_commands(context)
setup_events(context)

client.run(TOKEN)
