import discord
from context import BotContext


def setup(context: BotContext):
    tree = context.tree
    helper_utils = context.helper_utils

    @tree.command(
        name="betterrename",
        description="Changes the name of a user",
    )
    async def betterrename(
        interaction: discord.Interaction,
        member: discord.Member,
        new_name: str,
        reason: str,
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
                guild,
                "renames",
                executor,
                punished_member,
                "rename",
                f"'{member.display_name}' -> '{new_name}'\n{reason}",
            )

            await punished_member.edit(nick=new_name)

            try:
                await interaction.response.send_message(
                    f"Successfully renamed '{member.mention}' to '{new_name}'.",
                    ephemeral=True,
                )
            except Exception as e:
                print(e)
        else:
            await interaction.response.send_message(
                f"❌ go away you cant do that", ephemeral=True
            )
