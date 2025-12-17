import discord
from context import BotContext


def setup(context: BotContext):
    tree = context.tree
    database = context.database

    @tree.command(name="reset_guild_settings")
    async def reset_guild_settings(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return
        database.server.create_server_document(interaction.guild)
        await interaction.response.send_message(
            f"All guild settings have been reset", ephemeral=True
        )
