import discord
from context import BotContext


def setup(context: BotContext):
    tree = context.tree
    database = context.database

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
