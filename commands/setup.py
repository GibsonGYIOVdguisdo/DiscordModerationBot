from context import BotContext

from commands.punishments.ban import setup as setup_ban
from commands.punishments.unban import setup as setup_unban
from commands.punishments.mute import setup as setup_mute
from commands.punishments.warn import setup as setup_warn
from commands.punishments.note import setup as setup_note
from commands.punishments.punishments import setup as setup_punishments

from commands.settings.reset import setup as setup_reset
from commands.settings.role_trust import setup as setup_role_trust
from commands.settings.role_value import setup as setup_role_value
from commands.settings.get_settings import setup as setup_get_settings
from commands.settings.get_member_info import setup as setup_get_member_info
from commands.settings.set_log_channel import setup as setup_set_log_channel


def setup_commands(context: BotContext):
    setup_ban(context)
    setup_unban(context)
    setup_mute(context)
    setup_warn(context)
    setup_note(context)
    setup_punishments(context)

    setup_reset(context)
    setup_role_trust(context)
    setup_role_value(context)
    setup_get_settings(context)
    setup_get_member_info(context)
    setup_set_log_channel(context)
