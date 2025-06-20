import discord
from database import Database
from helper_utils import HelperUtils
from collections import defaultdict
import asyncio

class BanRequestView(discord.ui.View):
    def __init__(self, client, executor: discord.Member, member: discord.Member, reason: str, evidence: str, helper_utils: HelperUtils):
        super().__init__(timeout=None)
        self.helper_utils = helper_utils
        self.client = client
        self.executor = executor
        self.member = member
        self.evidence = evidence
        self.reason = reason
        self.request_message = None
        self.member_value = helper_utils.get_member_value(member)

        executor_trust = helper_utils.get_weighted_member_trust(executor)
        self.approvers = set([executor.id])
        self.deniers = set([executor.id])
        self.trust = executor_trust

        self._auto_delete_task = asyncio.create_task(self.auto_delete_after_24h())

    async def auto_delete_after_24h(self):
        twenty_four_hours = 24 * 60 * 60
        await asyncio.sleep(twenty_four_hours)
        if self.request_message:
            try:
                await self.request_message.delete()
            except Exception:
                pass
    
    def register_ban_approval(self, member: discord.Member):
        self.trust += self.helper_utils.get_weighted_member_trust(member)
        self.approvers.add(member.id)

    async def register_ban_denial(self, member: discord.Member):
        self.trust -= self.helper_utils.get_weighted_member_trust(member)
        self.deniers.add(member.id)

    def has_member_voted(self, member: discord.Member):
        has_member_approved = member.id in self.approvers
        has_member_denied = member.id in self.deniers
        has_member_voted = has_member_approved or has_member_denied
        return has_member_voted

    @discord.ui.button(label="Approve Ban", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        punished_member = self.member
        guild = interaction.guild
        approver = interaction.guild.get_member(interaction.user.id)

        if not approver:
            await interaction.response.send_message("Could not retrieve your member data.", ephemeral=True)
            return
        
        if approver.id == self.executor.id:
            await interaction.response.send_message("You cannot approve your own ban.", ephemeral=True)
            return
        
        approver_trust = self.helper_utils.get_weighted_member_trust(approver)

        if approver_trust < 0:
            await interaction.response.send_message("You do not have permission to approve bans.", ephemeral=True)
            return
        
        if approver.id in self.has_member_voted(approver):
            await interaction.response.send_message("You have already voted on this ban.", ephemeral=True)
            return
        
        self.register_ban_approval(approver)

        if self.trust >= self.member_value:
            await self.member.ban(reason=self.reason)
            await interaction.response.send_message(f"{self.member.mention} has been banned.", ephemeral=True)
            await self.helper_utils.log_punishment(guild, "bans", self.executor, punished_member, "ban", self.reason, evidence_link=self.evidence, approvers=list(self.approvers))
            del self.approval_data
            await self.request_message.delete()
        else:
            await self.request_message.edit(
                content=f"{self.executor.mention} requested a ban on {self.member.mention}. Trust required: {self.member_value}. Current trust: {self.trust} / {self.member_value}. Reason: '{self.reason}'. Evidence: {self.evidence}. Approve below."
            )
            await interaction.response.send_message(
                f"Approval recorded. Current trust: {self.trust} / {self.member_value}. More approvals needed.",
                ephemeral=True
            )
    
    @discord.ui.button(label="Deny Ban", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        denying_member = interaction.guild.get_member(interaction.user.id)

        if not denying_member:
            await interaction.response.send_message("Could not retrieve your member data.", ephemeral=True)
            return
        
        denying_member_trust = self.helper_utils.get_weighted_member_trust(denying_member)

        if denying_member_trust < 0:
            await interaction.response.send_message("You do not have permission to approve bans.", ephemeral=True)
            return
        
        if denying_member.id == self.executor.id:
            await interaction.response.send_message(f"Ban request for {self.member.mention} has been cancelled.", ephemeral=True)
            await self.request_message.delete() 
            return
        
        if self.has_member_voted(denying_member):
            await interaction.response.send_message("You have already voted on this ban.", ephemeral=True)
            return
        
        self.register_ban_denial(denying_member)
        
        if self.trust < 0:
            await self.request_message.delete() 
            await interaction.response.send_message(f"Ban request for {self.member.mention} has been cancelled due to low trust.", ephemeral=True)
            return
        
        await self.request_message.edit(
            content=f"{self.executor.mention} requested a ban on {self.member.mention}. Trust required: {self.member_value}. Current trust: {self.trust} / {self.member_value}. Reason: '{self.reason}'. Approve below."
        )
        
        await interaction.response.send_message(f"Ban request for {self.member.mention} has been denied.", ephemeral=True)