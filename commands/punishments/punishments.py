import discord
from context import BotContext
from datetime import datetime, timezone, timedelta


def setup(context: BotContext):
    tree = context.tree
    helper_utils = context.helper_utils

    @tree.command(
        name="punishments",
    )
    async def punishments(
        interaction: discord.Interaction,
        member: discord.Member = None,
        member_id: str = "-1",
        all_punishments: bool = False,
        show_ids: bool = False,
        page: int = 1,
    ):
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        executor_trust = helper_utils.trust.get_member_trust(executor)
        if not helper_utils.member.is_staff_member(executor):
            await interaction.response.send_message(
                "You do not have permission", ephemeral=True
            )
            return
        if not member and member_id == "-1":
            await interaction.response.send_message(
                "Please provide a member or member id", ephemeral=True
            )
            return

        after = None
        if not all_punishments:
            after = datetime.now(timezone.utc) - timedelta(days=14)

        embed = helper_utils.logs.get_punishment_embed(
            guild, member, int(member_id), after=after, show_ids=show_ids, page=page
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
