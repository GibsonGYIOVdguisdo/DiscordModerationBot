import discord
from context import BotContext


def setup(context: BotContext):
    tree = context.tree
    database = context.database

    @tree.command(name="set_role_value")
    async def set_role_value(
        interaction: discord.Interaction, role: discord.Role, value: int
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        database.server.set_role_value(interaction.guild, role, value)
        await interaction.response.send_message(
            f"Value of '{role}' set to '{value}'", ephemeral=True
        )
