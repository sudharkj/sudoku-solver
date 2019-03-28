# sudoku/__init__.py
import copy

from sudoku.constraint import Constraint
from sudoku.rule import Rule
from utils.status import Status

cols = [[i, 0] for i in range(9)]
rows = [[0, i] for i in range(9)]
grids = [[i, j] for i in range(3) for j in range(3)]
RULE_MASK = 0
for mask in range(10):
    RULE_MASK |= (1 << mask)


def get_allowed_tuples(length):
    """
    Iteratively build and return allowed tuples with given length.
    :param length: length of each tuples
    :return: allowed tuples
    """
    if length == 0:
        return []

    tuples = [[n] for n in range(1, 10)]
    for l in range(length - 1):
        tuples = [t + [n] for t in tuples for n in range(t[-1] + 1, 10) if n not in t]
    return tuples


class SuDoKu:
    """
    Class to save and solve a SuDoKu puzzle.
    """
    def __init__(self, name, board):
        self._name = name
        self._constraints = [[Constraint((i, j)) for j in range(9)] for i in range(9)]
        self._board = [[0 for _ in range(9)] for _ in range(9)]
        self._status = Status.UN_SOLVED

        for i in range(9):
            for j in range(9):
                if board[i][j] > 0:
                    self._set_cell((i, j), board[i][j], 0)
        self._original = copy.deepcopy(self._board)

    @property
    def name(self):
        return self._name

    @property
    def status(self):
        """
        Sets and returns the status of the puzzle if it is not {@link Status#UN_SOLVED}.
        :return: status of the puzzle
        """
        if self._status is Status.UN_SOLVED:
            res = Status.SOLVED

            # rows
            for i in range(9):
                res = max(res, self._get_block_status([i, 0], rows))
            # cols
            for j in range(9):
                res = max(res, self._get_block_status([0, j], cols))
            # grid
            for i in range(0, 9, 3):
                for j in range(0, 9, 3):
                    res = max(res, self._get_block_status([i, j], grids))

            self._status = res
        return self._status

    def _get_block_status(self, start, block):
        """
        Check status of a block.
        :param start: start index of the block
        :param block: list of index differences from the start
        :return: status of the block
        """
        # puzzle is invalid if an unfilled cell cannot be filled by any number
        for diff in block:
            xt, yt = start[0] + diff[0], start[1] + diff[1]
            if self._board[xt][yt] == 0 and len(self._constraints[xt][yt].allowed) == 0:
                return Status.IN_VALID

        # find the frequency of each number in a block
        freq = [0 for _ in range(10)]
        for diff in block:
            xt, yt = start[0] + diff[0], start[1] + diff[1]
            freq[self._board[xt][yt]] = freq[self._board[xt][yt]] + 1

        if freq[0] > 0:
            # puzzle is not yet solved if there are cells that are not filled
            return Status.UN_SOLVED
        for f in freq:
            if f > 1:
                # puzzle is invalid state if the block is filled with same number more than once
                return Status.IN_VALID
        # puzzle is solved in all other cases
        return Status.SOLVED

    def solve(self, bound=1000, rule_mask=RULE_MASK):
        """
        Solve the puzzle with incremental addition of allowed higher rules.
        :param bound: maximum number of actions
        :param rule_mask: masked rules
        :return: number of forward and backward steps and the number of branches
        """
        shift = -1
        allowed_rules = 0
        forward, backward, splits = 0, 0, 0

        while forward + backward < bound and self.status is not Status.SOLVED \
                and shift <= len(Rule.__members__.items()):
            shift += 1
            rule_value = rule_mask & (1 << shift)
            if rule_value == 0:
                continue

            allowed_rules |= rule_value

            front, back, sp = self._solve_mask(bound, allowed_rules)
            forward += front
            backward += back
            splits += sp

        if self.status is not Status.SOLVED and forward + backward >= bound:
            # puzzle state is timeout when the number of steps are more than bound
            self._status = Status.TIME_OUT
        return forward, backward, splits

    def _solve_mask(self, bound, rule_mask):
        """
        Solve the puzzle with allowed higher rules.
        :param bound: maximum number of actions
        :param rule_mask: masked rules
        :return: number of forward and backward steps and the number of branches
        """
        forward, backward, splits = 0, 0, 0
        while forward + backward < bound and self.status is Status.UN_SOLVED:
            # solve the puzzle as long as it is not solved
            front, back, sp = self._fixed_baseline(rule_mask), 0, 0

            if front == 0:
                # search on most constrained variable only when there is no fixed baseline
                front, back, sp = self._most_constrained_variable(bound - forward - backward, rule_mask)

            forward += front
            backward += back
            splits += sp
        return forward, backward, splits

    def _fixed_baseline(self, rule_mask):
        """
        Set the cell value when the allowed number of integers is only one.
        :param rule_mask: masked rules
        :return: 1 if any such cell is available or 0
        """
        for i in range(9):
            for j in range(9):
                if len(self._constraints[i][j].allowed) == 1:
                    # set the cell value if only one is possible
                    self._set_cell((i, j), self._constraints[i][j].allowed[0], rule_mask)
                    return 1
        return 0

    def _most_constrained_variable(self, bound, rule_mask):
        """
        Search for the most contrained variable and apply dfs.
        :param bound: maximum number of actions
        :param rule_mask: masked rules
        :return: number of forward and backward steps and the number of branches
        """
        # save the original state
        cur_constraints = copy.deepcopy(self._constraints)
        cur_board = copy.deepcopy(self._board)

        # sort the constraints
        constraints = [col for row in self._constraints for col in row if len(col.allowed) > 0]
        constraints = sorted(constraints)

        forward, backward, splits = 0, 0, 0
        while len(constraints) > 0:
            interest = constraints.pop(0)
            for num in interest.allowed:
                self._set_cell(interest.cell, num, rule_mask)
                forward += 1
                splits += 1
                front, back, sp = self._solve_mask(bound - forward - backward, rule_mask)
                forward += front
                splits += sp

                if self.status is Status.IN_VALID:
                    backward += front

                    # made a wrong estimate of cell value so revert it
                    self._board = copy.deepcopy(cur_board)
                    self._constraints = copy.deepcopy(cur_constraints)
                    self._status = Status.UN_SOLVED
                else:
                    backward += back

                if self.status is not Status.UN_SOLVED or forward + backward >= bound:
                    # break when there is timeout
                    break
        return forward, backward, splits

    def _set_cell(self, point, value, rule_mask):
        """
        Update cell value and apply inference on constraints.
        :param point: cell index
        :param value: value of the cell
        :param rule_mask: rules to be used for inference
        """
        x, y = point
        self._board[x][y] = value
        self._constraints[x][y].allowed = []

        # set row constraints
        self._update_block_constraints([x, 0], rows, value)

        # set column constraints
        self._update_block_constraints([0, y], cols, value)

        # set grid constraints
        self._update_block_constraints([3 * int(x / 3), 3 * int(y / 3)], grids, value)

        self._apply_inference(rule_mask)

    def _update_block_constraints(self, start, block, value):
        """
        Update constraints on the block.
        :param start: start index of the block
        :param block: list of index differences from the start
        :param value: value to be removed from the constraints of cells in the block
        """
        for diff in block:
            xt, yt = start[0] + diff[0], start[1] + diff[1]
            if value in self._constraints[xt][yt].allowed:
                self._constraints[xt][yt].allowed.remove(value)

    def _apply_inference(self, rule_mask):
        """
        Apply inference with rule mask.
        :param rule_mask: masked rules
        """
        shift = 10
        while shift > 0:
            shift = shift - 1
            rule = rule_mask & (1 << shift)
            if rule == 0:
                continue

            tuples = get_allowed_tuples(shift + 1)

            # rows
            for i in range(9):
                self._apply_naked_block([i, 0], tuples, rows)
                self._apply_hidden_block([i, 0], tuples, rows)
            # cols
            for j in range(9):
                self._apply_naked_block([0, j], tuples, cols)
                self._apply_hidden_block([0, j], tuples, cols)
            # grid
            for i in range(0, 9, 3):
                for j in range(0, 9, 3):
                    self._apply_naked_block([i, j], tuples, grids)
                    self._apply_hidden_block([i, j], tuples, grids)

    def _apply_naked_block(self, start, tuples, block):
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
            if self._board[loc[0]][loc[1]] > 0:
                valid_tuple = False
            s = set(self._constraints[loc[0]][loc[1]].allowed)
            for ind in tuple[1:]:
                loc = locs[ind - 1]
                if self._board[loc[0]][loc[1]] > 0:
                    valid_tuple = False
                s = s.union(self._constraints[loc[0]][loc[1]].allowed)

            if valid_tuple and len(s) == len(tuple):
                for diff in block:
                    x, y = start[0] + diff[0], start[1] + diff[1]
                    lim_nums = set(self._constraints[x][y].allowed)
                    rem_nums = lim_nums.difference(s)
                    if len(rem_nums) > 0:
                        self._constraints[x][y].allowed = list(rem_nums)

    def _apply_hidden_block(self, start, tuples, block):
        """
        Apply hidden inference on each type of block
        :param start: start node
        :param tuples: allowed tuples
        :param block: where to apply the inference
        """
        locs = [set() for s in range(10)]
        for diff in block:
            x, y = start[0] + diff[0], start[1] + diff[1]
            for num in self._constraints[x][y].allowed:
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
                        lim_nums = set(self._constraints[x][y].allowed)
                        self._constraints[x][y].allowed = list(lim_nums.intersection(set(tuple)))
                    else:
                        lim_nums = set(self._constraints[x][y].allowed)
                        self._constraints[x][y].allowed = list(lim_nums.difference(set(tuple)))
