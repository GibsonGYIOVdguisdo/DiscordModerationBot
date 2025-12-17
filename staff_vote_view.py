import discord
from database.database_handler import DatabaseHandler
from helper_utils import HelperUtils
from collections import defaultdict
import asyncio

class StaffVoteView(discord.ui.View):
    request_message_content = "Vote started. Trust required: {trust_required}. Current trust: {current_trust}. Approve below."
    def __init__(self, helper_utils: HelperUtils, timeout: float, required_trust: int, vote_owner: discord.Member, request_message=None):
        super().__init__(timeout=timeout)
        self.vote_owner = vote_owner
        self.request_message = request_message
        self.helper_utils = helper_utils
        self.approvers = set([vote_owner.id])
        self.deniers = set()
        self.combined_trust = helper_utils.get_weighted_member_trust(vote_owner)
        self.required_trust = required_trust
        self._auto_delete_task = asyncio.create_task(self.auto_delete_after_24h())

    async def auto_delete_after_24h(self):
        twenty_four_hours = 24 * 60 * 60
        await asyncio.sleep(twenty_four_hours)
        if self.request_message:
            try:
                await self.request_message.delete()
            except Exception:
                pass
    
    def register_approval(self, member: discord.Member):
        self.combined_trust += self.helper_utils.get_weighted_member_trust(member)
        self.approvers.add(member.id)

    def register_denial(self, member: discord.Member):
        self.combined_trust -= self.helper_utils.get_weighted_member_trust(member)
        self.deniers.add(member.id)

    def has_member_voted(self, member: discord.Member):
        has_member_approved = member.id in self.approvers
        has_member_denied = member.id in self.deniers
        has_member_voted = has_member_approved or has_member_denied
        return has_member_voted
    
    async def pre_vote_checks(self, interaction: discord.Interaction):
        voter = interaction.guild.get_member(interaction.user.id)
        if not voter:
            await interaction.response.send_message("Could not retrieve your member data.", ephemeral=True)
            return False
        if self.has_member_voted(voter):
            await interaction.response.send_message("You have already voted on this.", ephemeral=True)
            return False
        if not self.helper_utils.is_staff_member(voter):
            await interaction.response.send_message("Only staff can vote on this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.pre_vote_checks(interaction):
            return
        approver = interaction.guild.get_member(interaction.user.id)
        self.register_approval(approver)
        await self.update_request_message()
        if self.combined_trust >= self.required_trust:
            await self.request_message.delete()
            await self.on_vote_approval_end(interaction)
        else:
            await self.on_approve(interaction)
        
    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        denier_id = interaction.user.id
        if denier_id == self.vote_owner.id:
            await interaction.response.send_message(
                f"Request has been deleted",
                ephemeral=True
            )
            await self.request_message.delete()
            return
        if not await self.pre_vote_checks(interaction):
            return
        denier = interaction.guild.get_member(denier_id)
        self.register_denial(denier)
        await self.update_request_message()
        if self.combined_trust < 0:
            await self.request_message.delete()
            await self.on_vote_denial_end(interaction)
        else:
            await self.on_deny(interaction)

    async def on_deny(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Denial recorded. Current trust: {self.combined_trust} / {self.required_trust}.",
            ephemeral=True
        )
    
    async def on_approve(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Approval recorded. Current trust: {self.combined_trust} / {self.required_trust}.",
            ephemeral=True
        )

    async def on_vote_denial_end(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Request cancelled due to low trust.",
            ephemeral=True
        )

    async def on_vote_approval_end(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Request ended due to successful vote.",
            ephemeral=True
        )
    
    async def update_request_message(self):
        new_message_content = self.request_message_content.replace("{trust_required}", str(self.required_trust))
        new_message_content = new_message_content.replace("{current_trust}", str(self.combined_trust))
        await self.request_message.edit(
            content=new_message_content
        )
