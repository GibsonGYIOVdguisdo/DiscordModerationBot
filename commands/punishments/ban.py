import discord
from discord import app_commands
from context import BotContext
from views.ban_request import BanRequest as BanRequestView


def setup(context: BotContext):
    tree = context.tree
    database = context.database
    helper_utils = context.helper_utils

    @tree.command(
        name="betterban",
        description="Ban a user from the server",
    )
    @app_commands.choices(evidence=helper_utils.EvidenceChoices)
    async def betterban(
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str,
        evidence: app_commands.Choice[str],
    ):
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        punished_member = member
        executor_trust = helper_utils.trust.get_weighted_member_trust(executor)
        member_value = helper_utils.value.get_member_value(punished_member)
        evidence_type = evidence.value

        if not helper_utils.member.is_staff_member(executor):
            await interaction.response.send_message(
                "You do not have permission", ephemeral=True
            )
            return

        if helper_utils.member.is_staff_member(punished_member):
            await interaction.response.send_message(
                "You can not ban staff members", ephemeral=True
            )
            return

        evidence_embed = await helper_utils.messages.get_evidence_embed(
            punished_member, evidence_type, interaction.channel
        )
        if executor_trust >= member_value:
            await member.ban(delete_message_days=1, reason=reason)
            try:
                await interaction.response.send_message(
                    f"{member.mention} has been banned", ephemeral=True
                )
            except Exception as e:
                print(e)
            await helper_utils.logs.log_punishment(
                guild, "bans", executor, punished_member, "ban", reason, evidence_embed
            )
        else:
            approval_channel_id = database.server.get_log_channel(guild, "ban-requests")
            approval_channel = guild.get_channel(approval_channel_id)
            evidence_link = await helper_utils.logs.log_evidence(guild, evidence_embed)
            view = BanRequestView(
                executor, punished_member, reason, evidence_link, context
            )
            view.request_message = await approval_channel.send("-", view=view)
            await view.update_request_message()

            await interaction.response.send_message(
                "Ban request submitted for approval.", ephemeral=True
            )
