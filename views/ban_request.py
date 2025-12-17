import discord
from database.database import Database
from helper_utils import HelperUtils
from collections import defaultdict
from views.staff_vote import StaffVote
import asyncio


class BanRequest(StaffVote):
    request_message_content = "{executor} requested a ban on {punished_member}. Trust required: {trust_required}. Current trust: {current_trust}. Evidence: {evidence}. Reason: '{reason}'. Approve below."

    def __init__(
        self,
        executor: discord.Member,
        punished_member: discord.Member,
        reason: str,
        evidence: str,
        helper_utils: HelperUtils,
        request_message: discord.Message = None,
    ):
        twenty_four_hours = 24 * 60 * 60
        self.evidence = evidence
        self.punished_member = punished_member
        self.reason = reason
        punished_member_value = helper_utils.get_member_value(punished_member)

        super().__init__(
            helper_utils,
            twenty_four_hours,
            punished_member_value,
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
        new_message_content = new_message_content.replace(
            "{evidence}", str(self.evidence)
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
        await self.helper_utils.log_punishment(
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
