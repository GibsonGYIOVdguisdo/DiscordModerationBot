from typing import TypedDict
from models.feedback import Feedback


class Punishment(TypedDict):
    guildId: int
    memberId: int
    punisherId: int
    punishment: str
    reason: str
    evidence: str
    approvers: list[str]
    feedback: list[Feedback]
    date: str
