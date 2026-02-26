from typing import TypedDict
from datetime import datetime


class Feedback(TypedDict):
    feedback: str
    feedbackGiverId: int
    trustRemoved: int
    date: datetime
