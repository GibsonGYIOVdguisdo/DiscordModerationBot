from pymongo import MongoClient
import discord
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from models.server import Server


class Server:
    value_cache = TTLCache(maxsize=100, ttl=3600)
    trust_cache = TTLCache(maxsize=100, ttl=3600)

    def __init__(self, mongo_client: MongoClient):
        self.mongo_client = mongo_client
        self.db = self.mongo_client["ModerationBot"]
        self.servers = self.db["servers"]

    def create_server_document(self, guild: discord.Guild) -> None:
        self.servers.find_one_and_delete({"guildId": guild.id})
        server_document: Server = {
            "guildId": guild.id,
            "roleTrusts": {},
            "roleValues": {},
            "logChannels": {},
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

    def set_log_channel(
        self, guild: discord.Guild, log_type: str, channel: discord.TextChannel
    ):
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

    def get_server_document(self, guild: discord.Guild) -> Server | None:
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        return server_document
