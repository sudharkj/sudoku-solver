# sudoku/constraints.py
class Constraint:
    """
    Constraint on each cell.
    """
    def __init__(self, point):
        self.cell = point
        self.allowed = [k for k in range(1, 10)]

    def __lt__(self, other):
        return len(self.allowed) < len(other.allowed)
