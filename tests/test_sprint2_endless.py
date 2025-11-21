import sys
import pathlib

# Ensure 'src' (package root) is on sys.path so we can import package modules
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from game import game as game_module
from game.economy import BalanceManager


def _flatten_ticket_nums(ticket):
    return [n for row in ticket for n in row if n is not None]


def test_endless_mode_simulation_persistent_balance(tmp_path):
    storage = tmp_path / "wallet.json"

    # Use small numbers for speed and determinism
    starting_balance = 10
    ticket_cost = 1
    line_prize = 5

    manager = BalanceManager(storage_path=storage, starting_balance=starting_balance, ticket_cost=ticket_cost, line_prize=line_prize)

    # Two rounds simulation: buy ticket, draw ticket numbers first to force quick Bingo
    rounds = 2
    expected_balance = starting_balance
    for r in range(rounds):
        # spend for ticket
        manager.spend_for_tickets()
        expected_balance -= ticket_cost

        # make a deterministic ticket
        ticket = game_module.generate_unique_tickets(1, seed=100 + r)[0]

        # create a drawer that yields all ticket numbers first
        drawer = game_module.NumberDrawer()
        ticket_nums = _flatten_ticket_nums(ticket)
        # build pool: ticket numbers first, then remaining numbers
        rest = [n for n in range(1, 91) if n not in ticket_nums]
        drawer._pool = ticket_nums + rest
        drawer._drawn = []

        drawn_set = set()
        # draw until bingo
        while True:
            n = drawer.draw_next()
            drawn_set.add(n)
            if game_module.check_bingo_complete(ticket, drawn_set):
                # award bingo
                manager.award_bingo()
                expected_balance += manager.bingo_prize
                break

    # reload manager to ensure persistence
    reloaded = BalanceManager(storage_path=storage, starting_balance=1, ticket_cost=ticket_cost)
    assert reloaded.get_balance() == expected_balance


def test_drawer_and_ticket_quick_bingo():
    # Generate ticket and ensure that when drawer pool starts with ticket numbers,
    # bingo occurs within exactly len(ticket_numbers) draws
    ticket = game_module.generate_unique_tickets(1, seed=42)[0]
    ticket_nums = _flatten_ticket_nums(ticket)

    drawer = game_module.NumberDrawer()
    rest = [n for n in range(1, 91) if n not in ticket_nums]
    drawer._pool = ticket_nums + rest
    drawer._drawn = []

    drawn_set = set()
    draws = 0
    while True:
        n = drawer.draw_next()
        draws += 1
        drawn_set.add(n)
        if game_module.check_bingo_complete(ticket, drawn_set):
            break

    assert draws <= len(ticket_nums)
