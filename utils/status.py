# utils/status.py
from enum import Enum


class Status(Enum):
    """
    Allowed states of a puzzle in the increasing order of persistence.
    """
    SOLVED = 0
    UN_SOLVED = 1
    IN_VALID = 2
    TIME_OUT = 3

    def __gt__(self, other):
        return self.value > other.value
