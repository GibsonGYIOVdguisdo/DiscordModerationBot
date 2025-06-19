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
        
    def create_server_document(self, guild: discord.Guild):
        self.servers.find_one_and_delete({"guildId": guild.id})
        server_document = {
            "guildId": guild.id
        }
        self.servers.insert_one(server_document)

    def set_role_trust(self, guild: discord.Guild, role: discord.Role, trust: int):
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["roleTrust"] = server_document.get("roleTrust", {})
        server_document["roleTrust"][str(role.id)] = trust
        self.servers.find_one_and_replace(filter, server_document)

    def get_role_trust(self, guild, role):
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["roleTrust"] = server_document.get("roleTrust", {})
        role_trust = server_document["roleTrust"].get(str(role.id), 0)
        return role_trust
    
    def set_role_value(self, guild: discord.Guild, role: discord.Role, trust: int):
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["roleValue"] = server_document.get("roleValue", {})
        server_document["roleValue"][str(role.id)] = trust
        self.servers.find_one_and_replace(filter, server_document)

    def get_role_value(self, guild, role):
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["roleValue"] = server_document.get("roleValue", {})
        role_trust = server_document["roleValue"].get(str(role.id), 0)
        return role_trust

        
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
    database.create_server_document(guild)
    
@tree.command(name="reset_guild_settings")
async def reset_guild_settings(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )
        return
    database.create_server_document(interaction.guild)
    await interaction.response.send_message(f"All guild settings have been reset", ephemeral=True)

@tree.command(name="set_role_trust")
async def set_role_trust(interaction: discord.Interaction, role: discord.Role, trust: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )
        return
    
    database.set_role_trust(interaction.guild, role, trust)
    await interaction.response.send_message(f"Trust of '{role}' set to '{trust}'", ephemeral=True)

@tree.command(name="set_role_value")
async def set_role_value(interaction: discord.Interaction, role: discord.Role, trust: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )
        return
    
    database.set_role_value(interaction.guild, role, trust)
    await interaction.response.send_message(f"Value of '{role}' set to '{trust}'", ephemeral=True)


client.run(TOKEN)