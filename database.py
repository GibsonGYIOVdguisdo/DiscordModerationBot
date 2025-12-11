from pymongo import MongoClient
import discord
from datetime import datetime, timedelta, timezone
from cachetools import cached, TTLCache
from cachetools.keys import hashkey

class Database:
    value_cache = TTLCache(maxsize=100, ttl=3600)
    trust_cache = TTLCache(maxsize=100, ttl=3600)

    def __init__(self, mongo_uri):
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client['ModerationBot']
        self.servers = self.db["servers"]
        self.punishments = self.db["punishments"]
        
    def create_server_document(self, guild: discord.Guild):
        self.servers.find_one_and_delete({"guildId": guild.id})
        server_document = {
            "guildId": guild.id
        }
        self.servers.insert_one(server_document)

    def set_role_trust(self, guild: discord.Guild, role: discord.Role, trust: int):
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["roleTrusts"] = server_document.get("roleTrusts", {})
        server_document["roleTrusts"][str(role.id)] = trust
        self.servers.find_one_and_replace(filter, server_document)

        key = hashkey(self, guild, role)
        self.get_role_trust.cache.pop(key, None)

    @cached(trust_cache)
    def get_role_trust(self, guild: discord.Guild, role: discord.Role) -> int:
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["roleTrusts"] = server_document.get("roleTrusts", {})
        role_trust = server_document["roleTrusts"].get(str(role.id), -1)
        return role_trust
    
    def set_role_value(self, guild: discord.Guild, role: discord.Role, trust: int):
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["roleValues"] = server_document.get("roleValues", {})
        server_document["roleValues"][str(role.id)] = trust
        self.servers.find_one_and_replace(filter, server_document)

        key = hashkey(self, guild, role)
        self.get_role_value.cache.pop(key, None)

    @cached(value_cache)
    def get_role_value(self, guild: discord.Guild, role: discord.Role) -> int:
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["roleValues"] = server_document.get("roleValues", {})
        role_value = server_document["roleValues"].get(str(role.id), -1)
        return role_value
    
    def set_log_channel(self, guild: discord.Guild, log_type: str, channel: discord.TextChannel):
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["logChannels"] = server_document.get("logChannels", {})
        server_document["logChannels"][log_type] = channel.id
        self.servers.find_one_and_replace(filter, server_document)

    def get_log_channel(self, guild: discord.Guild, log_type: str) -> int:
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["logChannels"] = server_document.get("logChannels", {})
        log_channel = server_document["logChannels"].get(log_type, -1)
        return log_channel
        
    def add_member_punishment(self, guild: discord.Guild, executing_member: discord.Member, punished_member: discord.Member, punishment: str, reason: str, evidence: str, approvers: list[str]=[]):
        punishment_document = {
            "guildId": guild.id,
            "memberId": punished_member.id,
            "punisherId": executing_member.id,
            "punishment": punishment,
            "reason": reason,
            "evidence": evidence,
            "approvers": approvers,
            "date": datetime.now()
        }
        self.punishments.insert_one(punishment_document)

    def get_member_punishments(self, guild: discord.Guild, member: discord.Member=None, member_id=-1, punisher: discord.Member=None) -> list[object]:
        filter = {"guildId": guild.id}
        if member or member_id:
            if (member):
                member_id = member.id
            filter["memberId"] = member_id
        if punisher:
            filter["punisherId"] = punisher.id
        punishment_list = list(self.punishments.find(filter).sort("date", 1))
        return punishment_list
    
    def get_recently_given_bans(self, guild: discord.Guild, member: discord.Member=None):
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_punishments = list(self.punishments.find({
            "guildId": guild.id,
            "punisherId": member.id,
            "punishment": "ban",
            "date": {"$gte": one_hour_ago}
        }))
        return recent_punishments
    
    def get_recently_given_approvals(self, guild: discord.Guild, member: discord.Member=None):
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_punishments = list(self.punishments.find({
            "guildId": guild.id,
            "punishment": "ban",
            "date": {"$gte": one_hour_ago},
            "approvers": {"$in": [member.id]}
        }))
        return recent_punishments
    
    def has_recent_mod_warn(self, guild: discord.Guild, member: discord.Member):
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        filter = {
            "guildId": guild.id,
            "memberId": member.id,
            "punishment": "mod warn",
            "date": {"$gte": one_week_ago}
        }

        recent_warnings = list(self.punishments.find(filter))
        return len(recent_warnings) != 0
    
    def get_server_document(self, guild: discord.Guild) -> object:
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        return server_document