import discord
from discord import app_commands
from context import BotContext
from datetime import datetime, timedelta


def setup(context: BotContext):
    tree = context.tree
    helper_utils = context.helper_utils

    @tree.command(
        name="bettermute",
        description="Mute a user in the server for a specified duration",
    )
    @app_commands.describe(
        member="The member to mute",
        duration="Duration of the mute",
        reason="Reason for the mute",
    )
    @app_commands.choices(
        duration=[
            app_commands.Choice(name="5 minutes", value="5m"),
            app_commands.Choice(name="6 hour", value="6h"),
            app_commands.Choice(name="24 hour", value="24h"),
        ],
        evidence=helper_utils.EvidenceChoices,
    )
    async def bettermute(
        interaction: discord.Interaction,
        member: discord.Member,
        duration: app_commands.Choice[str],
        reason: str,
        evidence: app_commands.Choice[str],
    ):
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        punished_member = member
        executor_trust = helper_utils.trust.get_member_trust(executor)
        member_trust = helper_utils.trust.get_member_trust(punished_member)

        if (
            helper_utils.member.is_staff_member(executor)
            and executor_trust > member_trust
        ):
            duration_mapping = {"5m": 5, "6h": 360, "24h": 1440}
            mute_minutes = duration_mapping.get(duration.value)
            evidence_type = evidence.value

            try:
                await member.send(
                    f"You have been muted in {interaction.guild.name} for '{reason}'"
                )
            except Exception as e:
                print(e)

            now = datetime.now()
            now += timedelta(minutes=mute_minutes)
            await member.timeout(now.astimezone())

            try:
                await interaction.response.send_message(
                    f"Successfully muted {member.mention} for {duration.name} due to '{reason}'.",
                    ephemeral=True,
                )
            except Exception as e:
                print(e)

            evidence_embed = await helper_utils.messages.get_evidence_embed(
                punished_member, evidence_type, interaction.channel
            )
            await helper_utils.logs.log_punishment(
                guild,
                "mutes",
                executor,
                punished_member,
                duration.name,
                reason,
                evidence_embed,
            )
        else:
            await interaction.response.send_message(
                f"❌ go away you cant do that", ephemeral=True
            )
