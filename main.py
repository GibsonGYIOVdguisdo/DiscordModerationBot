import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from database import Database
from events import setup_events
from commands import setup_commands
from helper_utils import HelperUtils

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
tree.clear_commands(guild=None)
database = Database(MONGO_URI)
helper_utils = HelperUtils(client, database)

setup_events(client, tree, database, helper_utils)
setup_commands(tree, database, helper_utils, client)

client.run(TOKEN)