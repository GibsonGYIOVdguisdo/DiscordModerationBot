import discord
from discord import app_commands
from database import Database
from helper_utils import HelperUtils
from datetime import datetime, timedelta, timezone
from collections import defaultdict

def setup_commands(tree: app_commands.CommandTree, database: Database, helper_utils: HelperUtils):
    pending_approvals = defaultdict(lambda: {"trust": 0, "approvers": set()})

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
            app_commands.Choice(name="Mutes", value="mutes"),
            app_commands.Choice(name="Evidence", value="evidence"),
            app_commands.Choice(name="Bans", value="bans"),
            app_commands.Choice(name="Ban Requests", value="ban-requests"),
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
            try:
                await punished_member.send(f"You have been warned in {interaction.guild.name} for '{reason}'")
            except Exception as e:
                print(e)
            await interaction.response.send_message(f"Successfully warned {punished_member.mention} for '{reason}'", ephemeral=True)
            evidence_type = evidence.value
            evidence_embed = await helper_utils.get_evidence_embed(punished_member, evidence_type, interaction.channel)
            await helper_utils.log_punishment(guild, "warns", executor, punished_member, "warning", reason, evidence_embed)
        else:
            await interaction.response.send_message("You do not have permission", ephemeral=True)

    @tree.command(
        name="bettermute",
        description="Mute a user in the server for a specified duration",
    )
    @app_commands.describe(
        member="The member to mute",
        duration="Duration of the mute",
        reason="Reason for the mute"
    )
    @app_commands.choices(
        duration=[
            app_commands.Choice(name="5 minutes", value="5m"),
            app_commands.Choice(name="6 hour", value="6h"),
            app_commands.Choice(name="24 hour", value="24h")
        ],
        evidence=helper_utils.EvidenceChoices
    )
    async def bettermute(interaction: discord.Interaction, member: discord.Member, duration: app_commands.Choice[str], reason: str, evidence: app_commands.Choice[str]):
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        punished_member = member
        executor_trust = helper_utils.get_member_trust(executor)
        member_trust = helper_utils.get_member_trust(punished_member)

        if executor_trust >= 0 and executor_trust > member_trust:
            duration_mapping = {
                "5m": 5,
                "6h": 360,
                "24h": 1440
            }
            mute_minutes = duration_mapping.get(duration.value)
            evidence_type = evidence.value

            try:
                await member.send(f"You have been muted in {interaction.guild.name} for '{reason}'")
            except Exception as e:
                print(e)

            now = datetime.now()
            now += timedelta(minutes=mute_minutes)
            await member.timeout(now.astimezone())
            

            await interaction.response.send_message(
                f"Successfully muted {member.mention} for {duration.name} due to '{reason}'.", ephemeral=True
            )
            
            evidence_embed = await helper_utils.get_evidence_embed(punished_member, evidence_type, interaction.channel)
            await helper_utils.log_punishment(guild, "mutes", executor, punished_member, duration.name, reason, evidence_embed)
        else:
            await interaction.response.send_message(f"❌ go away you cant do that", ephemeral=True)

    @tree.command(
        name="betterban",
        description="Ban a user from the server",
    )
    @app_commands.choices(
        evidence=helper_utils.EvidenceChoices
    )
    async def betterban(interaction: discord.Interaction, member: discord.Member, reason: str, evidence: app_commands.Choice[str]):
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        punished_member = member
        executor_trust = helper_utils.get_weighted_member_trust(executor)
        member_trust = helper_utils.get_member_trust(punished_member)
        member_value = helper_utils.get_member_value(punished_member)
        evidence_type = evidence.value

        if executor_trust < 0:
            await interaction.response.send_message("You do not have permission", ephemeral=True)
            return
        
        if member_trust >= 0:
            await interaction.response.send_message("You can not ban staff members", ephemeral=True)
            return
        
        if executor_trust >= member_value:
            await member.ban(delete_message_days=1, reason=reason)
            await interaction.response.send_message(f"{member.mention} has been banned", ephemeral=True)
            evidence_embed = await helper_utils.get_evidence_embed(punished_member, evidence_type, interaction.channel)
            await helper_utils.log_punishment(guild, "bans", executor, punished_member, "ban", reason, evidence_embed)



    @tree.command(
        name="punishments",
    )
    async def punishments(
        interaction: discord.Interaction,
        member: discord.Member = None,
        member_id: str = "-1"
    ):
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        executor_trust = helper_utils.get_member_trust(executor)
        if executor_trust >= 0:
            embed = helper_utils.get_punishment_embed(guild, member, int(member_id))
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission", ephemeral=True)
