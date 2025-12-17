from context import BotContext

from commands.punishments.ban import setup as setup_ban
from commands.punishments.unban import setup as setup_unban
from commands.punishments.mute import setup as setup_mute
from commands.punishments.warn import setup as setup_warn
from commands.punishments.note import setup as setup_note
from commands.punishments.punishments import setup as setup_punishments

from commands.settings import setup as setup_settings


def setup_commands(context: BotContext):
    setup_ban(context)
    setup_unban(context)
    setup_mute(context)
    setup_warn(context)
    setup_note(context)
    setup_punishments(context)
    setup_settings(context)
