from typing import TypedDict


class Punishment(TypedDict):
    guildId: int
    memberId: int
    punisherId: int
    punishment: str
    reason: str
    evidence: str
    approvers: list[str]
    date: str
