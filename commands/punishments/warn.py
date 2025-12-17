import discord
from discord import app_commands
from context import BotContext


def setup(context: BotContext):
    tree = context.tree
    helper_utils = context.helper_utils

    @tree.command(
        name="betterwarn",
        description="Sends a warning to a user",
    )
    @app_commands.choices(evidence=helper_utils.EvidenceChoices)
    async def betterwarn(
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str,
        evidence: app_commands.Choice[str],
    ):
        punished_member = member
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        executor_trust = helper_utils.trust.get_member_trust(executor)
        punished_member_trust = helper_utils.trust.get_member_trust(punished_member)
        if (
            helper_utils.member.is_staff_member(executor)
            and executor_trust > punished_member_trust
        ):
            try:
                await punished_member.send(
                    f"You have been warned in {interaction.guild.name} for '{reason}'"
                )
            except Exception as e:
                print(e)
            try:
                await interaction.response.send_message(
                    f"Successfully warned {punished_member.mention} for '{reason}'",
                    ephemeral=True,
                )
            except Exception as e:
                print(e)

            evidence_type = evidence.value
            evidence_embed = await helper_utils.messages.get_evidence_embed(
                punished_member, evidence_type, interaction.channel
            )
            await helper_utils.logs.log_punishment(
                guild,
                "warns",
                executor,
                punished_member,
                "warning",
                reason,
                evidence_embed,
            )
        else:
            await interaction.response.send_message(
                "You do not have permission", ephemeral=True
            )
