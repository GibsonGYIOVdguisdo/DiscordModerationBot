import discord
from context import BotContext


def setup(context: BotContext):
    tree = context.tree
    helper_utils = context.helper_utils

    @tree.command(
        name="betternote", description="Adds a note to a member without messaging them"
    )
    async def betternote(
        interaction: discord.Interaction, member: discord.Member, text: str
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
            await helper_utils.logs.log_punishment(
                guild, "notes", executor, punished_member, "note", text, ""
            )

            try:
                await interaction.response.send_message(
                    f"Successfully added note '{text}' to '{member.mention}'.",
                    ephemeral=True,
                )
            except Exception as e:
                print(e)
        else:
            await interaction.response.send_message(
                f"❌ go away you cant do that", ephemeral=True
            )
