import os
from pymongo import MongoClient
from dotenv import load_dotenv
import discord
from discord import app_commands

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set.")
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN environment variable is not set.")

class Database:
    def __init__(self, mongo_uri):
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client['ModerationBot']
        self.servers = self.db["servers"]
        
    async def create_server_document(self, guild:discord.Guild):
        self.servers.find_one_and_delete({"guildId": guild.id})
        server_document = {
            "guildId": guild.id
        }
        self.servers.insert_one(server_document)
        

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
database = Database(MONGO_URI)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@client.event
async def on_guild_join(guild):
    await database.create_server_document(guild)
    
@tree.command(name="reset_guild_settings")
async def reset_guild_settings(interaction: discord.Interaction):
    await database.create_server_document(interaction.guild)
    await interaction.response.send_message(f"All guild settings have been reset")

client.run(TOKEN)