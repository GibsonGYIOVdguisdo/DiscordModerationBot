import discord
from discord import app_commands
from context import BotContext


def setup(context: BotContext):
    tree = context.tree
    database = context.database

    @tree.command(name="set_log_channel")
    @app_commands.choices(
        log_type=[
            app_commands.Choice(name="Warns", value="warns"),
            app_commands.Choice(name="Mutes", value="mutes"),
            app_commands.Choice(name="Evidence", value="evidence"),
            app_commands.Choice(name="Bans", value="bans"),
            app_commands.Choice(name="Ban Requests", value="ban-requests"),
            app_commands.Choice(name="Unban Requests", value="unban-requests"),
            app_commands.Choice(name="Notes", value="notes"),
        ]
    )
    async def set_log_channel(
        interaction: discord.Interaction,
        log_type: app_commands.Choice[str],
        channel: discord.TextChannel,
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return
        database.server.set_log_channel(interaction.guild, log_type.value, channel)
        await interaction.response.send_message(
            f"Log channel for '{log_type.name}' set to {channel.jump_url}",
            ephemeral=True,
        )
