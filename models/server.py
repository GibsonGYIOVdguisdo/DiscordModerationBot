from typing import TypedDict


class Server(TypedDict):
    guildId: int
    roleTrusts: dict[str, int]
    roleValues: dict[str, int]
    logChannels: dict[str, int]
