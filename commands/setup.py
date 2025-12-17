import discord
from discord import app_commands
from context import BotContext

import commands.settings
import commands.punishments


def setup_commands(context: BotContext):
    commands.settings.setup(context)
    commands.punishments.setup(context)
