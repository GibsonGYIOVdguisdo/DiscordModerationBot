import discord
from datetime import datetime, timezone
from utils.trust import TrustUtils


class MemberUtils:
    def __init__(self, database, trust_utils=None):
        self.database = database
        self.trust_utils = trust_utils

    def is_staff_member(self, member: discord.Member) -> bool:
        staff_trust_threshold = 0
        if self.trust_utils:
            return self.trust_utils.get_member_trust(member) >= staff_trust_threshold
        else:
            # Fallback in case trust_utils is not available
            member_trust = -1
            for role in member.roles:
                role_trust = self.database.server.get_role_trust(member.guild, role)
                member_trust = max(member_trust, role_trust)
            return member_trust >= staff_trust_threshold

    def is_member_bot(self, member: discord.Member) -> bool:
        if member.name.startswith("hellen") and member.name[6:].isdigit():
            return True
        elif member.name.startswith("butt") and member.name[4:].isdigit():
            return True
        elif member.name.startswith("hellenbutt") and member.name[10:].isdigit():
            return True
        return False

    @classmethod
    def format_member_string(cls, member: discord.Member) -> str:
        return f"{member.name} ({member.id})"
