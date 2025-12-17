import discord
from context import BotContext


def setup(context: BotContext):
    tree = context.tree
    helper_utils = context.helper_utils

    @tree.command(name="get_member_info")
    async def get_member_info(interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"{helper_utils.member.format_member_string(member)}"
        )

        embed.add_field(
            name="Unweighted Trust", value=helper_utils.trust.get_member_trust(member)
        )
        embed.add_field(
            name="Weighted Trust",
            value=helper_utils.trust.get_weighted_member_trust(member),
        )
        embed.add_field(name="Value", value=helper_utils.value.get_member_value(member))

        await interaction.response.send_message(embed=embed, ephemeral=True)
