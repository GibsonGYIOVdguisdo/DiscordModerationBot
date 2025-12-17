import discord


class TrustUtils:
    def __init__(self, database):
        self.database = database

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
        trust_reduction = recent_ban_count + recent_approval_count
        weighted_trust = max(member_trust - trust_reduction, 0)
        return weighted_trust

    def count_recent_approvals(self, member: discord.Member) -> int:
        guild = member.guild
        approved_punishments = self.database.punishment.get_recently_given_approvals(
            guild, member
        )
        return len(approved_punishments)

    def count_recently_given_bans(self, member: discord.Member) -> int:
        guild = member.guild
        punishments = self.database.punishment.get_recently_given_bans(guild, member)
        return len(punishments)
