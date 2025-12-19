from database.database import Database
from utils.utils import HelperUtils
from discord import Client
from discord.app_commands import CommandTree


class BotContext:
    def __init__(
        self,
        database: Database,
        helper_utils: HelperUtils,
        client: Client,
        tree: CommandTree,
    ):
        self.database = database
        self.helper_utils = helper_utils
        self.client = client
        self.tree = tree
