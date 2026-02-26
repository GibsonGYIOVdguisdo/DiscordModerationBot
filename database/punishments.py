from pymongo import MongoClient
import discord
from datetime import datetime, timedelta, timezone
from models.punishment import Punishment as PunishmentType
from models.feedback import Feedback
from bson.objectid import ObjectId


class Punishment:

    def __init__(self, mongo_client: MongoClient):
        self.mongo_client = mongo_client
        self.db = self.mongo_client["ModerationBot"]
        self.punishments = self.db["punishments"]

    def add_member_punishment(
        self,
        guild: discord.Guild,
        executing_member: discord.Member,
        punished_member: discord.Member,
        punishment: str,
        reason: str,
        evidence: str,
        approvers: list[str] = [],
    ):
        punishment_document: PunishmentType = {
            "guildId": guild.id,
            "memberId": punished_member.id,
            "punisherId": executing_member.id,
            "punishment": punishment,
            "reason": reason,
            "evidence": evidence,
            "approvers": approvers,
            "date": datetime.now(),
        }
        self.punishments.insert_one(punishment_document)

    def get_member_punishments(
        self,
        guild: discord.Guild,
        member: discord.Member = None,
        member_id=-1,
        punisher: discord.Member = None,
    ) -> list[object]:
        filter = {"guildId": guild.id}
        if member or member_id:
            if member:
                member_id = member.id
            filter["memberId"] = member_id
        if punisher:
            filter["punisherId"] = punisher.id
        punishment_list = list(self.punishments.find(filter).sort("date", 1))
        return punishment_list

    def get_recently_given_bans(
        self, guild: discord.Guild, member: discord.Member = None
    ):
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_punishments = list(
            self.punishments.find(
                {
                    "guildId": guild.id,
                    "punisherId": member.id,
                    "punishment": "ban",
                    "date": {"$gte": one_hour_ago},
                }
            )
        )
        return recent_punishments

    def get_recently_given_approvals(
        self, guild: discord.Guild, member: discord.Member = None
    ):
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_punishments = list(
            self.punishments.find(
                {
                    "guildId": guild.id,
                    "punishment": "ban",
                    "date": {"$gte": one_hour_ago},
                    "approvers": {"$in": [member.id]},
                }
            )
        )
        return recent_punishments

    def has_recent_mod_warn(self, guild: discord.Guild, member: discord.Member):
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        filter = {
            "guildId": guild.id,
            "memberId": member.id,
            "punishment": "mod warn",
            "date": {"$gte": one_week_ago},
        }

        recent_warnings = list(self.punishments.find(filter))
        return len(recent_warnings) != 0

    def get_punishment(self, guild: discord.Guild, punishment_id) -> PunishmentType:
        return self.punishments.find_one({"_id": ObjectId(punishment_id)})

    def add_punishment_feedback(
        self,
        guild: discord.Guild,
        punishment_id,
        feedback_giver: discord.Member,
        feedback: str,
        removed_trust: int = 0,
    ):
        filter = {"_id": ObjectId(punishment_id)}
        punishment: PunishmentType = self.punishments.find_one(filter)
        if not punishment:
            return False
        if not punishment.get("guildId", 0) == guild.id:
            return False
        feedback_object: Feedback = {
            "feedback": feedback,
            "feedbackGiverId": feedback_giver.id,
            "trustRemoved": removed_trust,
            "date": datetime.now(),
        }

        punishment["feedback"] = punishment.get("feedback", [])
        punishment["feedback"].append(feedback_object)

        self.punishments.find_one_and_replace(filter, punishment)

        return True
