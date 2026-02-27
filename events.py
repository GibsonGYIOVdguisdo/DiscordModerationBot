import discord
from discord import app_commands
from context import BotContext
from views.ban_suspicious_user import BanSuspiciousMembers as SuspiciousMemberView


def setup_events(context: BotContext):
    client = context.client
    database = context.database
    helper_util = context.helper_utils
    tree = context.tree

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user}")
        try:
            synced = await tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def check_if_suspicious(member):
        if helper_util.member.is_suspicious(member):
            guild = member.guild
            suspicious_member_channel_id = database.server.get_log_channel(
                member.guild, "suspicious-members"
            )
            suspicious_member_channel = guild.get_channel(suspicious_member_channel_id)
            evidence_embed = await helper_util.messages.get_evidence_embed(
                member, "profile"
            )
            evidence_link = await helper_util.logs.log_evidence(guild, evidence_embed)
            executor = member.guild.get_member(client.user.id)
            view = SuspiciousMemberView(
                executor, member, "Suspicious Member/Likely Bot", evidence_link, context
            )
            view.request_message = await suspicious_member_channel.send(
                "-", view=view, embed=evidence_embed
            )
            await view.update_request_message()
            return True
        return False

    @client.event
    async def on_guild_join(guild):
        database.server.create_server_document(guild)

    @client.event
    async def on_member_join(member: discord.Member):
        try:
            await member.guild.fetch_member(member.id)
        except discord.HTTPException:
            print(f"Failed to fetch {member.name}")
        if helper_util.member.is_member_bot(member):
            executing_member = member.guild.get_member(client.user.id)
            await member.ban(reason="bot")
            evidence_embed = await helper_util.messages.get_evidence_embed(
                member, "profile"
            )
            await helper_util.logs.log_punishment(
                member.guild,
                "bans",
                executing_member,
                member,
                "ban",
                "Bot",
                evidence_embed,
            )
        else:
            await check_if_suspicious(member)

    @client.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        member = message.author
        if helper_util.messages.is_message_from_bot(message):
            await member.ban(reason="bot")
            evidence_embed = await helper_util.messages.get_evidence_embed(
                member, "profile"
            )
            await helper_util.logs.log_punishment(
                member.guild,
                "bans",
                member,
                member,
                "ban",
                "Bot",
                evidence_embed,
            )

        if helper_util.messages.is_message_public_mod_talk(message):
            await helper_util.messages.give_mod_talk_warning(
                member, message.jump_url, client
            )
