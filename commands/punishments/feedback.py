import discord
from context import BotContext


def setup(context: BotContext):
    tree = context.tree
    helper_utils = context.helper_utils

    @tree.command(name="feedback", description="Adds feedback to a punishment")
    async def feedback(
        interaction: discord.Interaction,
        punishment_id: str,
        feedback: str,
        remove_trust: bool = False,
    ):
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        executor_trust = helper_utils.trust.get_member_trust(executor)

        if not helper_utils.member.is_staff_member(executor):
            return await interaction.response.send_message(
                "❌ go away you cant do that", ephemeral=True
            )

        punishment = helper_utils.database.punishment.get_punishment(
            interaction.guild, punishment_id
        )
        if punishment.get("guildId", 0) != interaction.guild.id:
            return await interaction.response.send_message(
                "Punishment does not exist.",
                ephemeral=True,
            )

        punisher = guild.get_member(punishment["punisherId"])
        punisher_trust = helper_utils.trust.get_member_trust(punisher)
        if executor_trust <= punisher_trust:
            print(executor_trust, punisher_trust)
            return await interaction.response.send_message(
                "Not enough trust", ephemeral=True
            )

        trust_removed = 1 if remove_trust else 0
        helper_utils.database.punishment.add_punishment_feedback(
            interaction.guild, punishment_id, interaction.user, feedback, trust_removed
        )

        if helper_utils.member.is_staff_member(punisher):
            feedback_notification_text = f"The '{punishment.get("punishment", "Unknown Punishment")}' you gave '{punishment.get("memberId", "Unknown Id")}' for '{punishment.get("reason", "Unknown Reason")}' has received the following feedback.\n'{feedback}':"

            if trust_removed > 0:
                feedback_notification_text += (
                    f"\nYou have lost {trust_removed} trust due to this"
                )
            try:
                await punisher.send(feedback_notification_text)
            except Exception as e:
                print(e)

        try:
            await interaction.response.send_message(
                f"Successfully added feedback '{feedback}' to punishment with id '{punishment_id}'",
                ephemeral=True,
            )
        except Exception as e:
            print(e)
