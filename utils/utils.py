import discord
from discord import app_commands
import asyncio
from datetime import datetime, timezone
from database.database import Database
from utils.member import MemberUtils
from utils.trust import TrustUtils
from utils.value import ValueUtils
from utils.messages import MessageUtils
from utils.logs import LogUtils


class HelperUtils:
    EvidenceChoices = [
        app_commands.Choice(name="Messages", value="messages"),
        app_commands.Choice(name="This Ticket", value="ticket"),
        app_commands.Choice(name="Profile", value="profile"),
        app_commands.Choice(name="Trust me bro", value="trust-me-bro"),
    ]

    def __init__(self, client: discord.Client, database: Database):
        self.client = client
        self.database = database

        self.trust = TrustUtils(database)
        self.value = ValueUtils(database)
        self.member = MemberUtils(database, self.trust)
        self.messages = MessageUtils(database, self)
        self.logs = LogUtils(database, self.messages)
