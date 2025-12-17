import discord
from discord import app_commands
from database.database_handler import DatabaseHandler
from helper_utils import HelperUtils

import commands.settings
import commands.punishments

def setup_commands(tree: app_commands.CommandTree, database: DatabaseHandler, helper_utils: HelperUtils, client: discord.Client):
    commands.settings.setup(tree, database, helper_utils, client)
    commands.punishments.setup(tree, database, helper_utils, client)