import random
from typing import List, Optional, Set, FrozenSet

"""Clean bingo game utilities used by tests.

Exports:
- generate_ticket_9x3(rnd, seed) -> Grid
- generate_unique_tickets(count, seed) -> List[Grid]
- NumberDrawer: simple deterministic-friendly drawer with .draw_next()
- check_bingo_complete(ticket, drawn_set) -> bool

This module is intentionally small and deterministic when a seed is provided.
"""

Grid = List[List[Optional[int]]]


def _default_col_ranges():
    return [
        list(range(1, 10)),        # 1-9
        list(range(10, 20)),       # 10-19
        list(range(20, 30)),
        list(range(30, 40)),
        list(range(40, 50)),
        list(range(50, 60)),
        list(range(60, 70)),
        list(range(70, 80)),
        list(range(80, 91)),       # 80-90 inclusive
    ]


def generate_ticket_9x3(rnd: Optional[random.Random] = None, seed: Optional[int] = None) -> Grid:
    """Generate a single 9x3 UK-style bingo ticket.

    The ticket is a list of 3 rows, each row a list of 9 cells where empty
    cells are `None` and filled cells are integers. Exactly 15 numbers are
    present and each row contains exactly 5 numbers.
    """
    if rnd is None:
        rnd = random.Random(seed)

    col_ranges = _default_col_ranges()

    # Determine how many numbers per column: start with 1 per column, then
    # distribute the remaining (15 - 9 = 6) across columns not exceeding 3.
    counts = [1] * 9
    remaining = 15 - 9
    cols = list(range(9))
    while remaining > 0:
        c = rnd.choice(cols)
        if counts[c] < 3:
            counts[c] += 1
            remaining -= 1

    # Pick numbers for each column
    col_numbers = []
    for c in range(9):
        pool = list(col_ranges[c])
        nums = rnd.sample(pool, counts[c])
        nums.sort()
        col_numbers.append(nums)

    # Decide which rows get numbers for each column such that each row ends up
    # with exactly 5 numbers. Greedy assignment works: handle columns with 3
    # first (one per row), then 2, then 1, assigning to rows with smallest
    # current count.
    row_counts = [0, 0, 0]
    rows_for_col = [None] * 9

    # columns grouped by count
    cols_by_count = {1: [], 2: [], 3: []}
    for i, c in enumerate(counts):
        cols_by_count[c].append(i)

    # assign 3-number columns
    for c in cols_by_count[3]:
        rows_for_col[c] = [0, 1, 2]
        row_counts = [rc + 1 for rc in row_counts]

    # assign 2-number columns: choose two rows with smallest counts
    for c in cols_by_count[2]:
        idxs = sorted(range(3), key=lambda r: row_counts[r])[:2]
        rows_for_col[c] = idxs
        for r in idxs:
            row_counts[r] += 1

    # assign 1-number columns: choose the row with smallest count
    for c in cols_by_count[1]:
        r = min(range(3), key=lambda r: row_counts[r])
        rows_for_col[c] = [r]
        row_counts[r] += 1

    # sanity: each row should have exactly 5 numbers
    assert all(rc == 5 for rc in row_counts), f"unexpected row counts: {row_counts}"

    # build grid and place numbers per column; within a column numbers are
    # placed top-to-bottom according to row index ordering
    grid: Grid = [[None for _ in range(9)] for _ in range(3)]
    for c in range(9):
        assigned_rows = sorted(rows_for_col[c])
        nums = col_numbers[c]
        # place numbers in increasing row order to keep column sorted
        for r_idx, r in enumerate(assigned_rows):
            grid[r][c] = nums[r_idx]

    return grid


def ticket_numbers_set(ticket: Grid) -> FrozenSet[int]:
    return frozenset(n for row in ticket for n in row if n is not None)


def generate_unique_tickets(count: int, seed: Optional[int] = None) -> List[Grid]:
    rnd = random.Random(seed)
    tickets = []
    seen: Set[FrozenSet[int]] = set()
    attempts = 0
    while len(tickets) < count and attempts < count * 50:
        t = generate_ticket_9x3(rnd=rnd)
        s = ticket_numbers_set(t)
        if s not in seen:
            seen.add(s)
            tickets.append(t)
        attempts += 1
    if len(tickets) < count:
        raise RuntimeError("could not generate enough unique tickets")
    return tickets


def check_bingo_complete(ticket: Grid, drawn: Set[int]) -> bool:
    """Return True if all 15 numbers on `ticket` are in `drawn`."""
    nums = ticket_numbers_set(ticket)
    return nums.issubset(drawn)


class NumberDrawer:
    """Simple number drawer for 1..90. Tests may override internals for
    deterministic behavior by setting `._pool` and clearing `._drawn`.
    """

    def __init__(self, rnd: Optional[random.Random] = None):
        self.rnd = rnd or random.Random()
        self._pool = list(range(1, 91))
        self._drawn = []

    def draw_next(self) -> int:
        if not self._pool:
            raise StopIteration("no more numbers")
        # draw from front to allow tests to set pool order deterministically
        n = self._pool.pop(0)
        self._drawn.append(n)
        return n

    def drawn(self) -> List[int]:
        return list(self._drawn)

    def remaining(self) -> List[int]:
        return list(self._pool)

    def remaining_count(self) -> int:
        return len(self._pool)
