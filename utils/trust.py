import discord
from database.database import Database
from datetime import datetime, timedelta, timezone


class TrustUtils:
    def __init__(self, database):
        self.database: Database = database

    def get_member_trust(self, member: discord.Member) -> int:
        guild = member.guild
        member_trust = -1
        for role in member.roles:
            role_trust = self.database.server.get_role_trust(guild, role)
            member_trust = max(member_trust, role_trust)
        return member_trust

    def get_weighted_member_trust(self, member: discord.Member) -> int:
        member_trust = self.get_member_trust(member)
        recent_ban_count = self.count_recently_given_bans(member)
        recent_approval_count = self.count_recent_approvals(member)
        feedback_removal_amount = self.calculate_feedback_trust_removal(member)
        trust_reduction = (
            recent_ban_count + recent_approval_count + feedback_removal_amount
        )
        weighted_trust = max(member_trust - trust_reduction, 0)
        return weighted_trust

    def count_recent_approvals(self, member: discord.Member) -> int:
        guild = member.guild
        approved_punishments = self.database.punishment.get_recently_given_approvals(
            guild, member
        )
        return len(approved_punishments)

    def calculate_feedback_trust_removal(self, member: discord.Member) -> int:
        total_removed = 0
        two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
        guild = member.guild
        all_punishments = self.database.punishment.get_punishments_with_feedback(
            guild, member, two_weeks_ago
        )
        for punishment in all_punishments:
            for feedback in punishment.get("feedback", []):
                if feedback.get("date"):
                    aware_date = feedback.get("date")
                    aware_date = aware_date.replace(tzinfo=timezone.utc)
                    if aware_date > two_weeks_ago:
                        total_removed += feedback.get("trustRemoved", 0)
        return total_removed

    def count_recently_given_bans(self, member: discord.Member) -> int:
        guild = member.guild
        punishments = self.database.punishment.get_recently_given_bans(guild, member)
        return len(punishments)
