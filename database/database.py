from pymongo import MongoClient
import discord
from datetime import datetime, timedelta, timezone
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from database.punishments import Punishment
from database.servers import Server


class Database:
    value_cache = TTLCache(maxsize=100, ttl=3600)
    trust_cache = TTLCache(maxsize=100, ttl=3600)

    def __init__(self, mongo_uri):
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client["ModerationBot"]
        self.punishment = Punishment(self.mongo_client)
        self.server = Server(self.mongo_client)
