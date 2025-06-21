import discord
from discord import app_commands
from database import Database
import asyncio
from datetime import datetime, timedelta, timezone

class HelperUtils:
    EvidenceChoices = [
        app_commands.Choice(name="Messages", value="messages"),
        app_commands.Choice(name="This Ticket", value="ticket"),
        app_commands.Choice(name="Profile", value="profile"),
        app_commands.Choice(name="Trust me bro", value="trust-me-bro")
    ]
    
    def __init__(self, client: discord.Client, database: Database):
        self.client = client
        self.database = database

    def count_recent_approvals(self, member: discord.Member) -> int:
        guild = member.guild
        approved_punishments = self.database.get_recently_given_approvals(guild, member)
        return len(approved_punishments)

    def count_recently_given_bans(self, member: discord.Member) -> int:
        guild = member.guild
        punishments = self.database.get_recently_given_bans(guild, member)
        return len(punishments)

    def get_weighted_member_trust(self, member: discord.Member) -> int:
        member_trust = self.get_member_trust(member)
        recent_ban_count = self.count_recently_given_bans(member)
        recent_approval_count = self.count_recent_approvals(member)
        trust_reduction = recent_ban_count + recent_approval_count
        weighted_trust = max(member_trust - trust_reduction, 0)
        return weighted_trust

    def get_member_trust(self, member: discord.Member) -> int:
        guild = member.guild
        member_trust = -1
        for role in member.roles:
            role_trust = self.database.get_role_trust(guild, role)
            member_trust = max(member_trust, role_trust)
        return member_trust
    
    def is_staff_member(self, member: discord.Member) -> bool:
        staff_trust_threshold = 0
        is_staff_member = self.get_member_trust(member) >= staff_trust_threshold
        return is_staff_member
    
    def get_member_value(self, member: discord.Member) -> int:
        guild = member.guild
        member_value = 0
        if (datetime.now(timezone.utc) - member.joined_at).total_seconds() > 86400:
            member_value = 1
        for role in member.roles:
            role_trust = self.database.get_role_value(guild, role)
            member_value = max(member_value, role_trust)
        return member_value
    
    @classmethod
    def format_member_string(cls, member: discord.Member) -> str:
        return f"{member.name} ({member.id})"
        
    def get_punishment_embed(self, guild: discord.Guild, member: discord.Member = None, member_id: int = -1) -> discord.Embed:
        embed = discord.Embed(title=f"{member or member_id} punishments")
        punishment_list = self.database.get_member_punishments(guild, member, member_id)[-10:]
        for punishment in punishment_list:
            punishment_type = f"**{punishment['punishment']}**"
            reason = punishment["reason"]
            try:
                punisher = guild.get_member(punishment["punisherId"])
            except:
                punisher = "Left server"
            date = punishment["date"]
            evidence = punishment.get("evidence", "No evidence provided")
            punishment_text = f"**Reason**: {reason}\n**Punisher**: {punisher}\n**Date**: {date}\n**Evidence**: {evidence}"
            embed.add_field(name=punishment_type.upper(), value=punishment_text, inline=False)
        if len(punishment_list) == 0:
            embed.add_field(name="**No punishments**", value="")
        return embed

    async def log_evidence(self, guild, evidence_embed) -> str:
        evidence_message = "No evidence provided"
        if evidence_embed:
            evidence_channel_id = self.database.get_log_channel(guild, "evidence")
            evidence_channel = guild.get_channel(evidence_channel_id)
            evidence_message = (await evidence_channel.send(embed=evidence_embed)).jump_url
        return evidence_message

    async def log_punishment(self, guild: discord.Guild, log_type: str, executing_member: discord.Member, punished_member: discord.Member, punishment: str, reason: str, evidence_embed:discord.Embed=None, evidence_link:str="", approvers:list[id]=[]):
        log_channel_id = self.database.get_log_channel(guild, log_type)
        log_channel = guild.get_channel(log_channel_id) 

        evidence_message = "No evidence provided"
        if evidence_link:
            evidence_message = evidence_link
        elif evidence_embed:
            evidence_message = await self.log_evidence(guild, evidence_embed)

        embed = discord.Embed(title=punishment)
        embed.add_field(name="Member", value=HelperUtils.format_member_string(punished_member), inline=False)
        embed.add_field(name="Punisher", value=HelperUtils.format_member_string(executing_member), inline=False)
        embed.add_field(name="Punishment", value=punishment, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Evidence", value=evidence_message, inline=False)
        self.database.add_member_punishment(guild, executing_member, punished_member, punishment, reason, evidence_message, approvers)
        
        await log_channel.send(embed=embed)

    async def get_last_n_messages(self, channel: discord.TextChannel, member: discord.Member, count: int):
        all_messages = []
        async for message in channel.history(limit=100):
            if message.author == member:
                all_messages.append(message)
        all_messages = sorted(all_messages, key=lambda x: x.created_at)
        return all_messages[-count:]
    
    async def get_evidence_embed(self, member: discord.Member, type: str, channel: discord.TextChannel=None):
        embed = discord.Embed(title=f"{member} evidence", color=discord.Color.blue())
        attachments = []
        max_fields = 25
        if type == "messages":
            messages = await self.get_last_n_messages(channel, member, max_fields)
            for message in messages[::-1]:
                embed.add_field(name=message.jump_url, value=message.content, inline=False)
                for attachment in message.attachments:
                    attachments.append(await attachment.to_file())
            asyncio.create_task(channel.delete_messages(messages))
        elif type == "ticket":
            embed.add_field(name="Ticket Channel", value=channel.jump_url, inline=False)
            if "ticket" in channel.name:
                async for message in channel.history(limit=max_fields, oldest_first=True):
                    embed.add_field(name=str(message.author), value=message.content, inline=False)
                    for attachment in message.attachments:
                        attachments.append(await attachment.to_file())
        elif type == "trust-me-bro":
            return None
        elif type == "profile":
            embed.set_image(url=member.display_avatar.url)
            embed.add_field(name="Username", value=member.name, inline=False)
            embed.add_field(name="Display Name", value=member.global_name, inline=False)
            embed.add_field(name="Nickname", value=member.nick, inline=False)
            embed.add_field(name="Status", value=member.nick, inline=False)
        return embed