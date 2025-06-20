import discord
from database import Database
from helper_utils import HelperUtils
from collections import defaultdict

class ApprovalView(discord.ui.View):
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
        self.approval_data = {"trust": executor_trust, "approvers": set([executor.id])}
    
    def register_ban_approval(self, approver: discord.Member):
        self.approval_data["trust"] += self.helper_utils.get_weighted_member_trust(approver)
        self.approval_data["approvers"].add(approver.id)

    @discord.ui.button(label="Approve Ban", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        punished_member = self.member
        guild = interaction.guild
        approver = interaction.guild.get_member(interaction.user.id)
        approval_data = self.approval_data

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
        
        if approver.id in approval_data["approvers"]:
            await interaction.response.send_message("You have already approved this ban.", ephemeral=True)
            return
        
        self.register_ban_approval(approver)

        if approval_data["trust"] >= self.member_value:
            await self.member.ban(reason=self.reason)
            await interaction.response.send_message(f"{self.member.mention} has been banned.", ephemeral=True)
            await self.helper_utils.log_punishment(guild, "bans", self.executor, punished_member, "ban", self.reason, evidence_link=self.evidence, approvers=list(approval_data["approvers"]))
            del self.approval_data
            await self.request_message.delete()
        else:
            await self.request_message.edit(
                content=f"{self.executor.mention} requested a ban on {self.member.mention}. Trust required: {self.member_value}. Current trust: {approval_data['trust']} / {self.member_value}. Reason: '{self.reason}'. Evidence: {self.evidence}. Approve below."
            )
            await interaction.response.send_message(
                f"Approval recorded. Current trust: {approval_data['trust']} / {self.member_value}. More approvals needed.",
                ephemeral=True
            )