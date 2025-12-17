import discord
from discord import app_commands
from database.database import Database
from helper_utils import HelperUtils
from datetime import datetime, timedelta, timezone
from views.ban_request_view import BanRequestView
from views.unban_request_view import UnbanRequestView

def setup(tree: app_commands.CommandTree, database: Database, helper_utils: HelperUtils, client: discord.Client):
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
        if helper_utils.is_staff_member(executor) and executor_trust > punished_member_trust:
            try:
                await punished_member.send(f"You have been warned in {interaction.guild.name} for '{reason}'")
            except Exception as e:
                print(e)
            try:
                await interaction.response.send_message(f"Successfully warned {punished_member.mention} for '{reason}'", ephemeral=True)
            except Exception as e:
                print(e)
            
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

        if helper_utils.is_staff_member(executor) and executor_trust > member_trust:
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
            
            try:
                await interaction.response.send_message(
                    f"Successfully muted {member.mention} for {duration.name} due to '{reason}'.", ephemeral=True
                )
            except Exception as e:
                print(e)
            
            evidence_embed = await helper_utils.get_evidence_embed(punished_member, evidence_type, interaction.channel)
            await helper_utils.log_punishment(guild, "mutes", executor, punished_member, duration.name, reason, evidence_embed)
        else:
            await interaction.response.send_message(f"❌ go away you cant do that", ephemeral=True)

    @tree.command(
        name="betterunban",
        description="Unbans a user from the server",
    )
    async def betterunban(interaction: discord.Interaction, member_id: str, reason: str):
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        executor_trust = helper_utils.get_weighted_member_trust(executor)
        ban_entry = None 

        try:
            ban_entry = await interaction.guild.fetch_ban(discord.Object(id=int(member_id)))
        except discord.NotFound:
            await interaction.response.send_message("User not found or not banned.", ephemeral=True)
            return
            
        if not helper_utils.is_staff_member(executor):
            await interaction.response.send_message("You do not have permission", ephemeral=True)
            return
        
        minimum_trust_for_unban = 5
        if executor_trust >= minimum_trust_for_unban:
            await interaction.guild.unban(ban_entry.user, reason=f"Unbanned by {executor}. Reason: {reason}")
            try:
                await interaction.response.send_message(f"{ban_entry.user} has been unbanned", ephemeral=True)
            except Exception as e:
                print(e)
            await helper_utils.log_punishment(interaction.guild, "bans", executor, ban_entry.user, "unban", reason)
        else:
            approval_channel_id = database.server.get_log_channel(guild, "unban-requests")
            approval_channel = guild.get_channel(approval_channel_id)
            view = UnbanRequestView(executor, ban_entry, reason, helper_utils)
            view.request_message = await approval_channel.send(
                "-",
                view=view
            )
            await view.update_request_message()

            await interaction.response.send_message("Unban request submitted for approval.", ephemeral=True)

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
        member_value = helper_utils.get_member_value(punished_member)
        evidence_type = evidence.value

        if not helper_utils.is_staff_member(executor):
            await interaction.response.send_message("You do not have permission", ephemeral=True)
            return
        
        if helper_utils.is_staff_member(punished_member):
            await interaction.response.send_message("You can not ban staff members", ephemeral=True)
            return
        
        evidence_embed = await helper_utils.get_evidence_embed(punished_member, evidence_type, interaction.channel)
        if executor_trust >= member_value:
            await member.ban(delete_message_days=1, reason=reason)
            try:
                await interaction.response.send_message(f"{member.mention} has been banned", ephemeral=True)
            except Exception as e:
                print(e)
            await helper_utils.log_punishment(guild, "bans", executor, punished_member, "ban", reason, evidence_embed)
        else:
            approval_channel_id = database.server.get_log_channel(guild, "ban-requests")
            approval_channel = guild.get_channel(approval_channel_id)
            evidence_link = await helper_utils.log_evidence(guild, evidence_embed)
            view = BanRequestView(executor, punished_member, reason, evidence_link, helper_utils)
            view.request_message = await approval_channel.send(
                "-",
                view=view
            )
            await view.update_request_message()

            await interaction.response.send_message("Ban request submitted for approval.", ephemeral=True)

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
        if not helper_utils.is_staff_member(executor):
            await interaction.response.send_message("You do not have permission", ephemeral=True)
            return
        if not member and member_id == "-1":
            await interaction.response.send_message("Please provide a member or member id", ephemeral=True)
            return
        embed = helper_utils.get_punishment_embed(guild, member, int(member_id))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tree.command(
        name="betternote",
        description="Adds a note to a member without messaging them"
    )
    async def betternote(interaction: discord.Interaction, member: discord.Member, text: str):
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        punished_member = member

        executor_trust = helper_utils.get_member_trust(executor)
        member_trust = helper_utils.get_member_trust(punished_member)

        if helper_utils.is_staff_member(executor) and executor_trust > member_trust:
            await helper_utils.log_punishment(guild, "notes", executor, punished_member, "note", text, "")
            
            try:
                await interaction.response.send_message(
                    f"Successfully added note '{text}' to '{member.mention}'.", ephemeral=True
                )
            except Exception as e:
                print(e)
        else:
            await interaction.response.send_message(f"❌ go away you cant do that", ephemeral=True)