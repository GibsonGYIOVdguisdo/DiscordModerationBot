import discord
from discord import app_commands
from database import Database
from helper_utils import HelperUtils

def setup_events(client: discord.Client, tree: app_commands.CommandTree, database: Database, helper_util: HelperUtils):
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

    @client.event
    async def on_member_join(member: discord.Member):
        try:
            await member.guild.fetch_member(member.id)
        except discord.HTTPException:
            print(f"Failed to fetch {member.name}")