import discord
from datetime import datetime
from database.database import Database


class LogUtils:
    def __init__(self, database, message_utils):
        self.database: Database = database
        self.message_utils = message_utils

    def get_punishment_embed(
        self,
        guild: discord.Guild,
        member: discord.Member = None,
        member_id: int = -1,
        after: datetime = None,
        show_ids: bool = False,
        page=1,
    ) -> discord.Embed:
        embed = discord.Embed(title=f"{member or member_id}'s punishments\nPage {page}")
        punishment_list = self.database.punishment.get_member_punishments(
            guild, member, member_id, after=after
        )
        start = len(punishment_list) - (10 * page)
        end = len(punishment_list) - (10 * (page - 1))
        punishment_list = punishment_list[start:end]

        for punishment in punishment_list:
            punishment_type = f"**{punishment.get('punishment', 'unknown')}**"
            reason = punishment.get("reason", "")
            try:
                punisher = guild.get_member(punishment.get("punisherId", 0))
            except:
                punisher = punishment.get("punisherId", 0)
            date = punishment.get("date")
            id = punishment.get("_id", "ID INVALID")
            evidence = punishment.get("evidence", "No evidence provided")
            punishment_text = f"**Reason**: {reason}\n**Punisher**: {punisher}\n**Date**: {date}\n**Evidence**: {evidence}"
            if show_ids:
                punishment_text += f"\n**Id**: {id}"
            embed.add_field(
                name=punishment_type.upper(), value=punishment_text, inline=False
            )
        if len(punishment_list) == 0:
            embed.add_field(name="**No punishments**", value="")
        return embed

    async def log_evidence(self, guild, evidence_embed) -> str:
        evidence_message = "No evidence provided"
        if evidence_embed:
            evidence_channel_id = self.database.server.get_log_channel(
                guild, "evidence"
            )
            evidence_channel = guild.get_channel(evidence_channel_id)
            evidence_message = (
                await evidence_channel.send(embed=evidence_embed)
            ).jump_url
        return evidence_message

    async def log_punishment(
        self,
        guild: discord.Guild,
        log_type: str,
        executing_member: discord.Member,
        punished_member: discord.Member,
        punishment: str,
        reason: str,
        evidence_embed: discord.Embed = None,
        evidence_link: str = "",
        approvers: list[id] = [],
    ):
        log_channel_id = self.database.server.get_log_channel(guild, log_type)
        log_channel = guild.get_channel(log_channel_id)

        evidence_message = "No evidence provided"
        if evidence_link:
            evidence_message = evidence_link
        elif evidence_embed:
            evidence_message = await self.log_evidence(guild, evidence_embed)

        embed = discord.Embed(title=punishment)
        embed.add_field(
            name="Member",
            value=f"{punished_member.name} ({punished_member.id})",
            inline=False,
        )
        embed.add_field(
            name="Punisher",
            value=f"{executing_member.name} ({executing_member.id})",
            inline=False,
        )
        embed.add_field(name="Punishment", value=punishment, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Evidence", value=evidence_message, inline=False)
        self.database.punishment.add_member_punishment(
            guild,
            executing_member,
            punished_member,
            punishment,
            reason,
            evidence_message,
            approvers,
        )

        await log_channel.send(embed=embed)

    async def give_mod_talk_warning(self, member: discord.Member, evidence: str):
        guild = member.guild
        punisher = member.guild.get_member(self.database)

        self.database.punishment.add_member_punishment(
            guild, punisher, member, "mod warn", "Punishment related messages", evidence
        )
