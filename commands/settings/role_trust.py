import discord
from context import BotContext


def setup(context: BotContext):
    tree = context.tree
    database = context.database

    @tree.command(name="set_role_trust")
    async def set_role_trust(
        interaction: discord.Interaction, role: discord.Role, trust: int
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        database.server.set_role_trust(interaction.guild, role, trust)
        await interaction.response.send_message(
            f"Trust of '{role}' set to '{trust}'", ephemeral=True
        )
