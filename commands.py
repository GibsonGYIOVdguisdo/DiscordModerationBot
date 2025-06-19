import discord
from discord import app_commands
from database import Database
from helper_utils import HelperUtils

def setup_commands(tree: app_commands.CommandTree, database: Database, helper_utils: HelperUtils):
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

    @tree.command(
        name="set_log_channel",
    )
    @app_commands.choices(
        log_type=[
            app_commands.Choice(name="Warns", value="warns"),
            app_commands.Choice(name="Evidence", value="evidence"),
        ]
    )
    async def set_log_channel(interaction: discord.Interaction, log_type: app_commands.Choice[str], channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return
        database.set_log_channel(interaction.guild, log_type.value, channel)
        await interaction.response.send_message(f"Log channel for '{log_type.name}' set to {channel.jump_url}", ephemeral=True)

    @tree.command(
        name="betterwarn",
        description="Sends a warning to a user",
    )
    @app_commands.choices(
        evidence=helper_utils.EvidenceChoices
    )
    async def betterwarn(interaction: discord.Interaction, member: discord.Member, reason: str, evidence: app_commands.Choice[str]):
        punished_member = member
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        executor_trust = helper_utils.get_member_trust(executor)
        punished_member_trust = helper_utils.get_member_trust(punished_member)
        if executor_trust >= 0 and executor_trust > punished_member_trust:
            evidence_type = evidence.value
            evidence_embed = await helper_utils.get_evidence_embed(punished_member, evidence_type, interaction.channel)
            try:
                await punished_member.send(f"You have been warned in {interaction.guild.name} for '{reason}'")
            except Exception as e:
                print(e)
            await helper_utils.log_punishment(guild, "warns", executor, punished_member, "warning", reason, evidence_embed)
            await interaction.response.send_message(f"Successfully warned {punished_member.mention} for '{reason}'", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission", ephemeral=True)

    @tree.command(
        name="punishments",
    )
    async def punishments(
        interaction: discord.Interaction,
        member: discord.Member = None,
        member_id: int = None
    ):
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        executor_trust = helper_utils.get_member_trust(executor)
        if executor_trust >= 0:
            embed = helper_utils.get_punishment_embed(guild, member, member_id)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission", ephemeral=True)