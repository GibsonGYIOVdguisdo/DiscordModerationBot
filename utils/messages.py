import discord
import asyncio


class MessageUtils:
    def __init__(self, database, helper_utils=None):
        self.database = database
        self.helper_utils = helper_utils

    async def get_last_n_messages(
        self, channel: discord.TextChannel, member: discord.Member, count: int
    ):
        all_messages = []
        async for message in channel.history(limit=100):
            if message.author == member:
                all_messages.append(message)
        all_messages = sorted(all_messages, key=lambda x: x.created_at)
        return all_messages[-count:]

    async def get_evidence_embed(
        self, member: discord.Member, type: str, channel: discord.TextChannel = None
    ):
        embed = discord.Embed(title=f"{member} evidence", color=discord.Color.blue())
        attachments = []
        max_fields = 25
        if type == "messages":
            messages = await self.get_last_n_messages(channel, member, max_fields)
            for message in messages[::-1]:
                message_text = message.content
                for attachment in message.attachments:
                    message_text += "\n" + attachment.url
                embed.add_field(name=message.jump_url, value=message_text, inline=False)
            asyncio.create_task(channel.delete_messages(messages))
        elif type == "ticket":
            embed.add_field(name="Ticket Channel", value=channel.jump_url, inline=False)
            if "ticket" in channel.name:
                async for message in channel.history(
                    limit=max_fields - 1, oldest_first=True
                ):
                    message_text = message.content
                    for attachment in message.attachments:
                        message_text += "\n" + attachment.url
                    embed.add_field(
                        name=str(message.author), value=message_text, inline=False
                    )
        elif type == "trust-me-bro":
            return None
        elif type == "profile":
            embed.set_image(url=member.display_avatar.url)
            embed.add_field(name="Username", value=member.name, inline=False)
            embed.add_field(name="Display Name", value=member.global_name, inline=False)
            embed.add_field(name="Nickname", value=member.nick, inline=False)
            embed.add_field(name="Status", value=member.nick, inline=False)
        return embed

    def is_message_from_bot(self, message: discord.Message) -> bool:
        if not self.helper_utils:
            return False
        member = message.author
        member_value = self.helper_utils.value.get_member_value(member)
        if message.content == "DMs open for guy" and member_value <= 0:
            return True
        return False

    def is_message_public_mod_talk(self, message: discord.Message) -> bool:
        if not self.helper_utils:
            return False
        channel = message.channel
        member = message.author
        guild = member.guild

        keywords = ["ban", "mute", "warn", "punish"]

        if not self.helper_utils.member.is_staff_member(member):
            return False

        if self.database.punishment.has_recent_mod_warn(guild, member):
            return False

        everyone_role = message.guild.default_role
        if channel.permissions_for(everyone_role).read_messages:
            for keyword in keywords:
                if keyword in message.content:
                    return True
        return False

    async def give_mod_talk_warning(
        self, member: discord.Member, evidence: str, client: discord.Client
    ):
        if not self.helper_utils:
            return
        guild = member.guild
        punisher = guild.get_member(client.user.id)

        self.database.punishment.add_member_punishment(
            guild, punisher, member, "mod warn", "Punishment related messages", evidence
        )

        warning_text = "It looks like you might have been talking about punishments publicly. Please avoid talking about punishments (even if done by you) outside of staff chat and tickets to prevent problems."
        await member.send(warning_text)
