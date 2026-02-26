from typing import TypedDict


class Feedback(TypedDict):
    feedback: str
    feedbackGiverId: int
    trustRemoved: int
    date: str
