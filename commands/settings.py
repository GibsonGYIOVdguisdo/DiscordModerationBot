import discord
from discord import app_commands
from context import BotContext


def setup(context: BotContext):
    tree = context.tree
    database = context.database
    helper_utils = context.helper_utils
    client = context.client

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

    @tree.command(name="get_guild_settings")
    async def get_guild_settings(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return
        embed = discord.Embed(title=f"{interaction.guild.name} Settings")

        server_document = database.server.get_server_document(interaction.guild)

        trust_text = ""
        role_trusts = server_document.get("roleTrusts", {})
        for role in role_trusts:
            trust_text += f"<@&{role}>: {role_trusts[role]}\n"
        embed.add_field(name="**Role Trust**", value=trust_text)

        value_text = ""
        role_values = server_document.get("roleValues", {})
        for role in role_values:
            value_text += f"<@&{role}>: {role_values[role]}\n"
        embed.add_field(name="**Role Value**", value=value_text)

        log_text = ""
        log_channels = server_document.get("logChannels", {})
        for channel in log_channels:
            log_text += f"{channel}: {interaction.guild.get_channel(log_channels[channel]).jump_url}\n"
        embed.add_field(name="**Log Channels**", value=log_text)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tree.command(name="get_member_info")
    async def get_member_info(interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"{helper_utils.member.format_member_string(member)}"
        )

        embed.add_field(
            name="Unweighted Trust", value=helper_utils.trust.get_member_trust(member)
        )
        embed.add_field(
            name="Weighted Trust",
            value=helper_utils.trust.get_weighted_member_trust(member),
        )
        embed.add_field(name="Value", value=helper_utils.value.get_member_value(member))

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tree.command(
        name="set_log_channel",
    )
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
