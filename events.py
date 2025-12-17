import discord
from discord import app_commands
from context import BotContext


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
            await member.ban(reason="Sextortion bot")
            evidence_embed = await helper_util.messages.get_evidence_embed(
                member, "profile"
            )
            await helper_util.logs.log_punishment(
                member.guild,
                "bans",
                executing_member,
                member,
                "ban",
                "Sextortion Bot",
                evidence_embed,
            )

    @client.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        member = message.author
        if helper_util.messages.is_message_from_bot(message):
            await member.ban(reason="Sextortion bot")
            evidence_embed = await helper_util.messages.get_evidence_embed(
                member, "profile"
            )
            await helper_util.logs.log_punishment(
                member.guild,
                "bans",
                member,
                member,
                "ban",
                "Sextortion Bot",
                evidence_embed,
            )

        if helper_util.messages.is_message_public_mod_talk(message):
            await helper_util.messages.give_mod_talk_warning(
                member, message.jump_url, client
            )
