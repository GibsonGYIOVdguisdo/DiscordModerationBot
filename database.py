from pymongo import MongoClient
import discord

class Database:
    def __init__(self, mongo_uri):
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client['ModerationBot']
        self.servers = self.db["servers"]
        
    def create_server_document(self, guild: discord.Guild):
        self.servers.find_one_and_delete({"guildId": guild.id})
        server_document = {
            "guildId": guild.id
        }
        self.servers.insert_one(server_document)

    def set_role_trust(self, guild: discord.Guild, role: discord.Role, trust: int):
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["roleTrust"] = server_document.get("roleTrust", {})
        server_document["roleTrust"][str(role.id)] = trust
        self.servers.find_one_and_replace(filter, server_document)

    def get_role_trust(self, guild, role):
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["roleTrust"] = server_document.get("roleTrust", {})
        role_trust = server_document["roleTrust"].get(str(role.id), 0)
        return role_trust
    
    def set_role_value(self, guild: discord.Guild, role: discord.Role, trust: int):
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["roleValue"] = server_document.get("roleValue", {})
        server_document["roleValue"][str(role.id)] = trust
        self.servers.find_one_and_replace(filter, server_document)

    def get_role_value(self, guild, role):
        filter = {"guildId": guild.id}
        server_document = self.servers.find_one(filter)
        server_document["roleValue"] = server_document.get("roleValue", {})
        role_trust = server_document["roleValue"].get(str(role.id), 0)
        return role_trust