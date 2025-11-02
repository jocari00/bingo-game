import sys
import pathlib
import random


# Ensure 'src' (package root) is on sys.path so we can import game.main
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from game import main as ticket_module


def _col_ranges():
    return [
        range(1, 10),
        range(10, 20),
        range(20, 30),
        range(30, 40),
        range(40, 50),
        range(50, 60),
        range(60, 70),
        range(70, 80),
        range(80, 91),
    ]


def test_generate_ticket_shape_and_counts():
    grid = ticket_module.generate_ticket_9x3(seed=42)

    # grid shape
    assert len(grid) == 3
    for row in grid:
        assert len(row) == 9

    # total numbers and per-row counts
    numbers = [n for row in grid for n in row if n is not None]
    assert len(numbers) == 15
    for row in grid:
        assert sum(1 for v in row if v is not None) == 5

    # per-column counts 1..3
    for c in range(9):
        cnt = sum(1 for r in range(3) if grid[r][c] is not None)
        assert 1 <= cnt <= 3

    # numbers unique and in 1..90
    assert len(set(numbers)) == 15
    assert all(1 <= n <= 90 for n in numbers)


def test_column_ranges_and_sorted():
    grid = ticket_module.generate_ticket_9x3(seed=123)
    col_ranges = _col_ranges()

    for c in range(9):
        col_vals = [grid[r][c] for r in range(3) if grid[r][c] is not None]
        # all values fall into the column's allowed numeric range
        for v in col_vals:
            assert v in col_ranges[c]
        # values top-to-bottom must be sorted
        assert col_vals == sorted(col_vals)


def test_ticket_numbers_set_and_uniqueness():
    t = ticket_module.generate_ticket_9x3(seed=7)
    key = ticket_module.ticket_numbers_set(t)
    assert isinstance(key, frozenset)
    assert len(key) == 15

    # generate multiple unique tickets
    tickets = ticket_module.generate_unique_tickets(5, seed=2025)
    assert len(tickets) == 5
    keys = [ticket_module.ticket_numbers_set(x) for x in tickets]
    assert len({k for k in keys}) == 5


def test_generate_unique_tickets_deterministic_and_zero():
    a = ticket_module.generate_unique_tickets(3, seed=999)
    b = ticket_module.generate_unique_tickets(3, seed=999)
    # Ensure deterministic behavior for same seed: compare sets sequence
    a_keys = [ticket_module.ticket_numbers_set(x) for x in a]
    b_keys = [ticket_module.ticket_numbers_set(x) for x in b]
    assert a_keys == b_keys

    # zero count returns empty list
    assert ticket_module.generate_unique_tickets(0) == []
