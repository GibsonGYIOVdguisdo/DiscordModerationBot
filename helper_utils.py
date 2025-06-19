import discord
from discord import app_commands
from database import Database

class HelperUtils:
    def __init__(self, client: discord.Client, database: Database):
        self.client = client
        self.database = database

    def get_member_trust(self, member: discord.Member) -> int:
        guild = member.guild
        member_trust = -1
        for role in member.roles:
            role_trust = self.database.get_role_trust(guild, role)
            member_trust = max(member_trust, role_trust)
        return member_trust
    
    def get_member_value(self, member: discord.Member) -> int:
        guild = member.guild
        member_value = 0
        for role in member.roles:
            role_trust = self.database.get_role_value(guild, role)
            member_value = max(member_value, role_trust)
        return member_value
    
    @classmethod
    def format_member_string(cls, member: discord.Member) -> str:
        return f"{member.name} ({member.id})"
        
    def get_punishment_embed(self, guild: discord.Guild, member: discord.Member = None, member_id: int = -1) -> discord.Embed:
        if not member:
            member = member_id
        embed = discord.Embed(title=f"{member} punishments")
        punishment_list = self.database.get_member_punishments(guild, member, member_id)[:10]
        for punishment in punishment_list:
            punishment_type = f"**{punishment["punishment"]}**"
            reason = punishment["reason"]
            try:
                punisher = guild.get_member(punishment["punisherId"])
            except:
                punisher = "Left server"
            date = punishment["date"]
            punishment_text = f"**Reason**: {reason}\n**Punisher**: {punisher}\n**Date**: {date}"
            embed.add_field(name=punishment_type.upper(), value=punishment_text, inline=False)
        return embed
            

    async def log_punishment(self, guild: discord.Guild, log_type: str, executing_member: discord.Member, punished_member: discord.Member, punishment: str, reason: str):
        log_channel_id = self.database.get_log_channel(guild, log_type)
        log_channel = guild.get_channel(log_channel_id)
        embed = discord.Embed(title=punishment)

        embed.add_field(name="member", value=HelperUtils.format_member_string(punished_member), inline=False)
        embed.add_field(name="punisher", value=HelperUtils.format_member_string(executing_member), inline=False)
        embed.add_field(name="punishment", value=punishment, inline=False)
        embed.add_field(name="reason", value=reason, inline=False)
        self.database.add_member_punishment(guild, executing_member, punished_member, punishment, reason)
        
        await log_channel.send(embed=embed)

