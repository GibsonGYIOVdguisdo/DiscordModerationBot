import discord
from datetime import datetime, timezone


class ValueUtils:
    def __init__(self, database):
        self.database = database

    def get_member_value(self, member: discord.Member) -> int:
        guild = member.guild
        member_value = 0
        if (datetime.now(timezone.utc) - member.joined_at).total_seconds() > 86400:
            member_value = 1
        for role in member.roles:
            role_value = self.database.server.get_role_value(guild, role)
            member_value = max(member_value, role_value)
        return member_value
