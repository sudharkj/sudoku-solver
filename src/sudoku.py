from enum import Enum
import copy


class Rule(Enum):
    NONE = 0
    SINGLES = 1
    PAIRS = 2
    TRIPLES = 4


class Constraint:
    def __init__(self, point):
        self.cell = point
        self.allowed = [k for k in range(1, 10)]

    def __lt__(self, other):
        return len(self.allowed) < len(other.allowed)


cols = [[i, 0] for i in range(9)]
rows = [[0, i] for i in range(9)]
grids = [[i, j] for i in range(3) for j in range(3)]


def get_allowed_tuples(length):
    if length == 0:
        return []

    tuples = [[n] for n in range(1, 10)]
    for l in range(length - 1):
        tuples = [t + [n] for t in tuples for n in range(t[-1] + 1, 10) if n not in t]
    return tuples


class Sudoku:
    def __init__(self, name, board):
        self.name = name
        self.constraints = [[Constraint((i, j)) for j in range(9)] for i in range(9)]
        self.board = [[0 for j in range(9)] for i in range(9)]
        self.back = 0

        for i in range(9):
            for j in range(9):
                if board[i][j] > 0:
                    self.set_cell((i, j), board[i][j], 0)

    def is_valid(self):
        # rows
        res = 0

        for i in range(9):
            res = max(res, self.is_valid_block([i, 0], rows))
        # cols
        for j in range(9):
            res = max(res, self.is_valid_block([0, j], cols))
        # grid
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                res = max(res, self.is_valid_block([i, j], grids))

        return res

    def is_valid_block(self, start, block):
        freq = [0 for i in range(10)]
        for diff in block:
            xt, yt = start[0] + diff[0], start[1] + diff[1]
            freq[self.board[xt][yt]] = freq[self.board[xt][yt]] + 1
        if freq[0] > 0:
            return 0
        for f in freq:
            if f > 1:
                return 2
        return 1

    def solve(self, bound=1000, rule_mask=0):
        steps = 0
        advanced = 0
        while steps < bound:
            advanced = self.solve_fixed_baseline(rule_mask)

            if advanced == 0:
                advanced = self.solve_most_constrained_variable(bound - steps, rule_mask)

            if advanced <= 0:
                break
            steps = steps + advanced
        return steps if advanced >= 0 else advanced

    def solve_fixed_baseline(self, rule_mask):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0 and len(self.constraints[i][j].allowed) == 0:
                    # check for any previous wrong move
                    return -1
                if len(self.constraints[i][j].allowed) == 1:
                    # set the cell value if only one is possible
                    return self.set_cell((i, j), self.constraints[i][j].allowed[0], rule_mask)
        return 0

    def solve_most_constrained_variable(self, bound, rule_mask):
        cur_constraints = copy.deepcopy(self.constraints)
        cur_board = copy.deepcopy(self.board)

        constraints = [col for row in self.constraints for col in row if len(col.allowed) > 0]
        constraints = sorted(constraints)
        while len(constraints) > 0:
            interest = constraints.pop(0)
            for num in interest.allowed:
                self.set_cell(interest.cell, num, rule_mask)
                value = self.solve(bound - 1, rule_mask)

                if value < 0:
                    self.back = self.back + 1
                    # illegal cell update is done so revert it
                    self.board = copy.deepcopy(cur_board)
                    self.constraints = copy.deepcopy(cur_constraints)
                else:
                    return value
        return 0

    def set_cell(self, point, value, rule_mask):
        x, y = point
        if value not in self.constraints[x][y].allowed:
            print('hacking')
        self.board[x][y] = value
        self.constraints[x][y].allowed = []

        # set row constraints
        self.update_block_constraints([x, 0], rows, value)

        # set column constraints
        self.update_block_constraints([0, y], cols, value)

        # set grid constraints
        self.update_block_constraints([3 * int(x/3), 3 * int(y/3)], grids, value)

        self.apply_inference(rule_mask)
        return 1

    def update_block_constraints(self, start, block, value):
        for diff in block:
            xt, yt = start[0] + diff[0], start[1] + diff[1]
            if value in self.constraints[xt][yt].allowed:
                self.constraints[xt][yt].allowed.remove(value)

    def apply_inference(self, rule_mask):
        length = 3
        while length > 0:
            length = length - 1
            rule = rule_mask & (1 << length)
            if rule == 0:
                continue

            tuples = get_allowed_tuples(length + 1)

            # rows
            for i in range(9):
                self.apply_naked_block([i, 0], tuples, rows)
                self.apply_hidden_block([i, 0], tuples, rows)
            # cols
            for j in range(9):
                self.apply_naked_block([0, j], tuples, cols)
                self.apply_hidden_block([0, j], tuples, cols)
            # grid
            for i in range(0, 9, 3):
                for j in range(0, 9, 3):
                    self.apply_naked_block([i, j], tuples, grids)
                    self.apply_hidden_block([i, j], tuples, grids)

    def apply_naked_block(self, start, tuples, block):
        """
        Apply naked inference on each type of block
        :param start: start node
        :param tuples: allowed tuples
        :param block: where to apply the inference
        """
        locs = []
        for diff in block:
            locs.append((start[0] + diff[0], start[1] + diff[1]))

        # intersection on allowed tuples
        for tuple in tuples:
            valid_tuple = True

            ind = tuple[0] - 1
            loc = locs[ind]
            if self.board[loc[0]][loc[1]] > 0:
                valid_tuple = False
            s = set(self.constraints[loc[0]][loc[1]].allowed)
            for ind in tuple[1:]:
                loc = locs[ind - 1]
                if self.board[loc[0]][loc[1]] > 0:
                    valid_tuple = False
                s = s.union(self.constraints[loc[0]][loc[1]].allowed)

            if valid_tuple and len(s) == len(tuple):
                for diff in block:
                    x, y = start[0] + diff[0], start[1] + diff[1]
                    lim_nums = set(self.constraints[x][y].allowed)
                    rem_nums = lim_nums.difference(s)
                    if len(rem_nums) > 0:
                        self.constraints[x][y].allowed = list(rem_nums)

    def apply_hidden_block(self, start, tuples, block):
        """
        Apply hidden inference on each type of block
        :param start: start node
        :param tuples: allowed tuples
        :param block: where to apply the inference
        """
        locs = [set() for s in range(10)]
        for diff in block:
            x, y = start[0] + diff[0], start[1] + diff[1]
            for num in self.constraints[x][y].allowed:
                locs[num].add((x, y))

        # intersection on allowed tuples
        for tuple in tuples:
            valid_tuple = True

            if len(locs[tuple[0]]) == 0:
                valid_tuple = False
            s = locs[tuple[0]]
            for num in tuple[1:]:
                if len(locs[num]) == 0:
                    valid_tuple = False
                s = s.union(locs[num])

            if valid_tuple and len(s) == len(tuple):
                for diff in block:
                    x, y = start[0] + diff[0], start[1] + diff[1]
                    if (x, y) in s:
                        lim_nums = set(self.constraints[x][y].allowed)
                        self.constraints[x][y].allowed = list(lim_nums.intersection(set(tuple)))
                    else:
                        lim_nums = set(self.constraints[x][y].allowed)
                        self.constraints[x][y].allowed = list(lim_nums.difference(set(tuple)))
