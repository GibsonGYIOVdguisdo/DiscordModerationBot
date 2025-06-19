from pymongo import MongoClient
import discord
from datetime import datetime

class Database:
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
        
    def add_member_punishment(self, guild: discord.Guild, executing_member: discord.Member, punished_member: discord.Member, punishment: str, reason: str):
        punishment_document = {
            "guildId": guild.id,
            "memberId": punished_member.id,
            "punisherId": executing_member.id,
            "punishment": punishment,
            "reason": reason,
            "date": datetime.now()
        }
        self.punishments.insert_one(punishment_document)

    def get_member_punishments(self, guild, member):
        filter = {
            "guildId": guild.id, 
            "memberId": member.id
        }
        self.punishments.find(filter)