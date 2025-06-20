import discord
from database import Database
from helper_utils import HelperUtils
from collections import defaultdict
from staff_vote_view import StaffVoteView
import asyncio

class UnbanRequestView(StaffVoteView):
    request_message_content = "{executor} requested an unban for {punished_member}. Trust required: {trust_required}. Current trust: {current_trust}. Reason: '{reason}'. Approve below."
    
    def __init__(self, executor: discord.Member, ban_entry: discord.BanEntry, reason: str, evidence: str, helper_utils: HelperUtils, request_message:discord.Message=None):
        twenty_four_hours = 24*60*60
        self.evidence = evidence
        self.ban_entry = ban_entry
        self.reason = reason

        minimum_trust_for_unban = 5
        super().__init__(helper_utils, twenty_four_hours, minimum_trust_for_unban, executor, request_message)

    async def update_request_message(self):
        new_message_content = self.request_message_content.replace("{executor}", str(self.vote_owner))
        new_message_content = new_message_content.replace("{punished_member}", str(self.punished_member))
        new_message_content = new_message_content.replace("{trust_required}", str(self.required_trust))
        new_message_content = new_message_content.replace("{current_trust}", str(self.combined_trust))
        new_message_content = new_message_content.replace("{evidence}", str(self.evidence))
        new_message_content = new_message_content.replace("{reason}", str(self.reason))

        await self.request_message.edit(
            content=new_message_content
        )

    async def on_vote_denial_end(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Unban request on {self.punished_member} cancelled due to low trust",
            ephemeral=True
        )

    async def on_vote_approval_end(self, interaction: discord.Interaction):
        await self.ban_entry.par(delete_message_days=1)
        await self.helper_utils.log_punishment(interaction.guild, "bans", self.vote_owner, self.punished_member, "unban", self.reason)
        await interaction.guild.unban(self.ban_entry.user, reason=f"Unban approved by staff. Requested by {self.vote_owner}. Reason: {self.reason}")
        
        await interaction.response.send_message(
            f"Unbanned {self.ban_entry.user}",
            ephemeral=True
        )