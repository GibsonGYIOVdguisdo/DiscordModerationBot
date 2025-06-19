import discord
from discord import app_commands
from database import Database


def setup_commands(tree: app_commands.CommandTree, database: Database):
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