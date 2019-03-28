# sudoku/rule.py
from enum import Enum


class Rule(Enum):
    """
    Class having all the allowed trick names.
    """
    NONE = 0
    SINGLES = 1
    PAIRS = 2
    TRIPLES = 4
    QUADS = 8
    PENTS = 16
    HEXES = 32
    SEPTS = 64
    OCTAS = 124
    NINE = 248
