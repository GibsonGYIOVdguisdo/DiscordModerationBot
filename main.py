import os
from dotenv import load_dotenv
import discord
from database import Database
from discord import app_commands

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