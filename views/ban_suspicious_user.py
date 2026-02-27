import discord
from context import BotContext
from collections import defaultdict
from views.staff_vote import StaffVote
import asyncio


class BanSuspiciousMembers(StaffVote):
    request_message_content = "{punished_member} has been flagged as suspicious. Approve this if they should be banned. Trust required: {trust_required}. Current trust: {current_trust}."

    def __init__(
        self,
        executor: discord.Member,
        punished_member: discord.Member,
        reason: str,
        evidence: str,
        context: BotContext,
        request_message: discord.Message = None,
    ):
        twenty_four_hours = 24 * 60 * 60
        self.punished_member = punished_member
        self.reason = reason
        required_trust = 1
        self.evidence = evidence

        super().__init__(
            context,
            twenty_four_hours,
            required_trust,
            executor,
            request_message,
        )

    async def update_request_message(self):
        new_message_content = self.request_message_content.replace(
            "{executor}", str(self.vote_owner)
        )
        new_message_content = new_message_content.replace(
            "{punished_member}", str(self.punished_member)
        )
        new_message_content = new_message_content.replace(
            "{trust_required}", str(self.required_trust)
        )
        new_message_content = new_message_content.replace(
            "{current_trust}", str(self.combined_trust)
        )
        new_message_content = new_message_content.replace("{reason}", str(self.reason))

        await self.request_message.edit(content=new_message_content)

    async def on_vote_denial_end(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Ban request on {self.punished_member} cancelled due to low trust",
            ephemeral=True,
        )

    async def on_vote_approval_end(self, interaction: discord.Interaction):
        await self.punished_member.ban(delete_message_days=1)
        await self.helper_utils.logs.log_punishment(
            interaction.guild,
            "bans",
            self.vote_owner,
            self.punished_member,
            "ban",
            self.reason,
            evidence_link=self.evidence,
            approvers=list(self.approvers),
        )
        await interaction.response.send_message(
            f"{self.punished_member} has been banned", ephemeral=True
        )
