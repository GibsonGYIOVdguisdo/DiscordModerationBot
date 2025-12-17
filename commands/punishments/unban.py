import discord
from context import BotContext
from views.unban_request import UnbanRequest as UnbanRequestView


def setup(context: BotContext):
    tree = context.tree
    database = context.database
    helper_utils = context.helper_utils

    @tree.command(
        name="betterunban",
        description="Unbans a user from the server",
    )
    async def betterunban(
        interaction: discord.Interaction, member_id: str, reason: str
    ):
        guild = interaction.guild
        executor = interaction.guild.get_member(interaction.user.id)
        executor_trust = helper_utils.trust.get_weighted_member_trust(executor)
        ban_entry = None

        try:
            ban_entry = await interaction.guild.fetch_ban(
                discord.Object(id=int(member_id))
            )
        except discord.NotFound:
            await interaction.response.send_message(
                "User not found or not banned.", ephemeral=True
            )
            return

        if not helper_utils.member.is_staff_member(executor):
            await interaction.response.send_message(
                "You do not have permission", ephemeral=True
            )
            return

        minimum_trust_for_unban = 5
        if executor_trust >= minimum_trust_for_unban:
            await interaction.guild.unban(
                ban_entry.user, reason=f"Unbanned by {executor}. Reason: {reason}"
            )
            try:
                await interaction.response.send_message(
                    f"{ban_entry.user} has been unbanned", ephemeral=True
                )
            except Exception as e:
                print(e)
            await helper_utils.logs.log_punishment(
                interaction.guild, "bans", executor, ban_entry.user, "unban", reason
            )
        else:
            approval_channel_id = database.server.get_log_channel(
                guild, "unban-requests"
            )
            approval_channel = guild.get_channel(approval_channel_id)
            view = UnbanRequestView(executor, ban_entry, reason, context)
            view.request_message = await approval_channel.send("-", view=view)
            await view.update_request_message()

            await interaction.response.send_message(
                "Unban request submitted for approval.", ephemeral=True
            )
