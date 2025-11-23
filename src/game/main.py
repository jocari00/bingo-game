import random
from typing import List, Optional, Set, FrozenSet

"""ticket_generator.py

Implements:
- generate_ticket_9x3: produce a single UK-style 9x3 ticket (15 numbers)
- generate_unique_tickets: produce multiple tickets ensuring uniqueness by number set
- print_ticket: improved terminal renderer
- NumberDrawer: draws numbers 1..90 without duplicates and keeps history

This file keeps the generator simple and testable. The original generator
logic is preserved but expanded to allow deterministic RNG injection.
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

    Args:
        rnd: optional random.Random instance to use (preferred for deterministic sequences).
        seed: optional int seed (used only if rnd is None).

    Returns:
        grid: 3x9 nested list, empty cells are None.

    The algorithm follows standard UK constraints:
    - exactly 15 numbers total
    - each row has exactly 5 numbers
    - each column has 1..3 numbers
    - numbers per column come from fixed ranges
    - numbers in each column are sorted top-to-bottom
    """
    if rnd is None:
        rnd = random.Random(seed)

    col_ranges = _default_col_ranges()

    TARGET_NUMBERS = 15
    ROWS = 3
    COLS = 9
    MAX_PER_COL = 3
    MIN_PER_COL = 1

    for attempt in range(1000):
        counts = [MIN_PER_COL] * COLS
        remaining = TARGET_NUMBERS - sum(counts)

        for _ in range(remaining):
            choices = [i for i in range(COLS) if counts[i] < MAX_PER_COL]
            if not choices:
                break
            c = rnd.choice(choices)
            counts[c] += 1

        if sum(counts) != TARGET_NUMBERS:
            continue

        try:
            col_numbers = [sorted(rnd.sample(col_ranges[i], counts[i])) for i in range(COLS)]
        except ValueError:
            continue

        capacities = [TARGET_NUMBERS // ROWS] * ROWS  # [5,5,5]
        grid: Grid = [[None for _ in range(COLS)] for _ in range(ROWS)]

        cols_order = sorted(range(COLS), key=lambda i: -counts[i])
        placement_failed = False

        for col in cols_order:
            k = counts[col]
            available_rows = [r for r in range(ROWS) if capacities[r] > 0]
            if len(available_rows) < k:
                placement_failed = True
                break
            chosen_rows = rnd.sample(available_rows, k)
            chosen_rows_sorted = sorted(chosen_rows)
            nums = col_numbers[col]
            for row_idx, num in zip(chosen_rows_sorted, nums):
                grid[row_idx][col] = num
                capacities[row_idx] -= 1

        if placement_failed:
            continue

        if all(cap == 0 for cap in capacities):
            return grid

    raise RuntimeError("Failed to generate a valid bingo ticket after many attempts.")


def ticket_numbers_set(grid: Grid) -> FrozenSet[int]:
    """Return the set of numbers present on a ticket as an immutable key.

    This is used to validate uniqueness across tickets (two tickets are
    considered identical if they contain the same 15 numbers regardless of position).
    """
    nums = {n for row in grid for n in row if n is not None}
    return frozenset(nums)


def generate_unique_tickets(count: int, seed: Optional[int] = None, max_attempts_per_ticket: int = 5000) -> List[Grid]:
    """Generate `count` unique tickets (unique by number-set) using a single RNG.

    Args:
        count: number of tickets to generate
        seed: optional seed for deterministic behavior
        max_attempts_per_ticket: how many retries to try per ticket before failing
    Returns:
        list of unique Grid objects
    Raises:
        RuntimeError if unable to produce the required number of unique tickets
    """
    if count <= 0:
        return []

    rnd = random.Random(seed)
    seen: Set[FrozenSet[int]] = set()
    tickets: List[Grid] = []

    for i in range(count):
        attempts = 0
        while attempts < max_attempts_per_ticket:
            # pass the RNG so sequences are deterministic and reproducible
            ticket = generate_ticket_9x3(rnd=rnd)
            key = ticket_numbers_set(ticket)
            if len(key) != 15:
                # sanity guard: regenerate if ticket malformed
                attempts += 1
                continue
            if key not in seen:
                seen.add(key)
                tickets.append(ticket)
                break
            attempts += 1

        if attempts >= max_attempts_per_ticket:
            raise RuntimeError(f"Failed to generate a unique ticket #{i+1} after {attempts} attempts")

    return tickets


def print_ticket(grid: Grid, drawn: Optional[Set[int]] = None, show_cols_header: bool = True) -> None:
    """Render a single 3x9 ticket clearly in the terminal.

    If `drawn` is provided (set of ints) drawn numbers are marked with a leading
    '*' so the player can see which numbers have been called.
    """
    COLS = 9
    if drawn is None:
        drawn = set()
    if show_cols_header:
        headers = " ".join(f" C{i}" for i in range(COLS))
        print(headers)
    # top border
    print("+" + "----" * COLS + "+")
    for row in grid:
        row_str = "|"
        for cell in row:
            if cell is None:
                row_str += "   |"
            else:
                if cell in drawn:
                    # mark drawn numbers with a leading '*'
                    row_str += f"*{cell:2d}|"
                else:
                    row_str += f" {cell:2d}|"
        print(row_str)
    # bottom border
    print("+" + "----" * COLS + "+")


def check_line_complete(grid: Grid, drawn: Set[int]) -> Optional[int]:
    """Check whether any single row (line) on `grid` is complete with respect to `drawn`.

    Returns the row index (0..2) of the first complete line found, or None if none.
    """
    for r, row in enumerate(grid):
        all_drawn = True
        for cell in row:
            if cell is None:
                continue
            if cell not in drawn:
                all_drawn = False
                break
        if all_drawn:
            return r
    return None


def validate_line_claim(grid: Grid, drawn: Set[int]) -> bool:
    """Validate a player's claim for a line. Returns True if a line is complete."""
    return check_line_complete(grid, drawn) is not None


def check_bingo_complete(grid: Grid, drawn: Set[int]) -> bool:
    """Return True if all numbers on `grid` are present in `drawn` (full ticket)."""
    for row in grid:
        for cell in row:
            if cell is None:
                continue
            if cell not in drawn:
                return False
    return True


def validate_bingo_claim(grid: Grid, drawn: Set[int]) -> bool:
    """Validate a player's Bingo claim (full ticket)."""
    return check_bingo_complete(grid, drawn)


def play_interactive_demo():
    """Interactive demo to buy one ticket, draw numbers, and allow manual line claims.

    Assumptions made:
    - Ticket cost is $1.
    - Valid line prize is $5.
    - Player starts with $10 by default (prompted).
    These choices are small, reasonable defaults for a demo and can be changed.
    """
    TICKET_COST = 1
    LINE_PRIZE = 5
    DEFAULT_WALLET = 10

    try:
        inp = input(f"Enter starting wallet amount (default {DEFAULT_WALLET}): ")
        wallet = int(inp) if inp.strip() else DEFAULT_WALLET
    except Exception:
        wallet = DEFAULT_WALLET

    print(f"You have ${wallet}. Each ticket costs ${TICKET_COST}.")
    if wallet < TICKET_COST:
        print("Insufficient funds to buy a ticket. Exiting demo.")
        return

    # Endless mode: keep playing rounds until the user explicitly exits with 'e'
    session_active = True
    while session_active:
        # Ensure the player can buy a ticket for this round
        if wallet < TICKET_COST:
            print("Insufficient funds to buy a ticket for the next round.")
            resp = input("Press 'e' to exit or press Enter to deposit and continue: ").strip().lower()
            if resp == 'e':
                break
            try:
                dep = int(input("Enter deposit amount: "))
                if dep > 0:
                    wallet += dep
                    print(f"Deposited ${dep}. Wallet: ${wallet}")
                else:
                    print("No deposit made.")
            except Exception:
                print("Invalid deposit. Exiting.")
                break
            if wallet < TICKET_COST:
                print("Still insufficient funds. Exiting.")
                break

        wallet -= TICKET_COST
        print(f"Bought 1 ticket for ${TICKET_COST}. Remaining wallet: ${wallet}\n")

        # Generate two unique tickets: one for the player and one for the bot
        tickets = generate_unique_tickets(2)
        player_ticket = tickets[0]
        bot_ticket = tickets[1]

        drawer = NumberDrawer()
        drawn_set: Set[int] = set()
        # player's manually marked numbers (player must confirm each draw)
        player_marked_set: Set[int] = set()

        # Track who (if anyone) has claimed the line or bingo for this round
        line_claimed_by: Optional[str] = None  # 'player' | 'bot' | None
        bingo_claimed_by: Optional[str] = None

        print("Your ticket:")
        # show player's own marked numbers (initially none)
        print_ticket(player_ticket, drawn=player_marked_set)
        print("(Bot has its own ticket.)")

        print("\nControls: press Enter to draw next number, 'l' to attempt to claim Line, 'b' to attempt to claim Bingo")

        round_active = True
        while round_active:
            try:
                n = drawer.draw_next()
            except StopIteration:
                print("No more numbers to draw for this round.")
                break
            drawn_set.add(n)
            print(f"\nNumber drawn: {n}")
            #print("Draw history:", drawer.drawn())

            # Ask player to manually confirm and mark the number on their ticket
            while True:
                mark_resp = input(f"Do you have {n} on your ticket? (y/n): ").strip().lower()
                if mark_resp in ("y", "n", ""):
                    break
                print("Please answer 'y' or 'n'.")

            if mark_resp == "y":
                # validate and mark if correct, else show error
                if n in ticket_numbers_set(player_ticket):
                    if n in player_marked_set:
                        print("That number is already marked on your ticket.")
                    else:
                        player_marked_set.add(n)
                        print(f"Marked {n} on your ticket.")
                else:
                    print("Error: that number is not on your ticket. No mark applied.")
            # show player's ticket with their own marks
            print_ticket(player_ticket, drawn=player_marked_set)

            # Check for line completion for both players: player uses their marked set, bot uses drawn_set
            player_line = check_line_complete(player_ticket, player_marked_set)
            bot_line = check_line_complete(bot_ticket, drawn_set)

            # If the bot completes a line and no one has claimed it yet, bot claims immediately
            if bot_line is not None and line_claimed_by is None:
                line_claimed_by = 'bot'
                print(f"Bot completed a LINE (row {bot_line}) and claims the ${LINE_PRIZE} line prize!")

            # If player attempts to claim line via input it will be validated against the current state
            resp = input("Claim? (Enter=continue, l=claim Line, b=claim Bingo): ").strip().lower()
            if resp == "l":
                # Only allow claim if no one has already claimed the line
                if line_claimed_by is not None:
                    print(f"Line already claimed by {line_claimed_by}. No prize for you.")
                    continue

                valid = validate_line_claim(player_ticket, player_marked_set)
                if valid:
                    line_claimed_by = 'player'
                    wallet += LINE_PRIZE
                    print(f"Valid LINE! You win ${LINE_PRIZE}. Wallet: ${wallet}\n")
                else:
                    print("Invalid claim — that is not a complete line. No prize awarded.")
                continue

            # Automatic bingo check: if either has bingo, award and end round
            player_bingo = check_bingo_complete(player_ticket, player_marked_set)
            bot_bingo = check_bingo_complete(bot_ticket, drawn_set)
            if player_bingo or bot_bingo:
                BINGO_PRIZE = LINE_PRIZE * 4

                # If bot has bingo and no one has claimed yet, bot wins immediately
                if bot_bingo and bingo_claimed_by is None:
                    bingo_claimed_by = 'bot'
                    print(f"Bot has BINGO and wins the ${BINGO_PRIZE} prize. You lose this round.")
                # Else if player has bingo and no one has claimed yet, player wins
                elif player_bingo and bingo_claimed_by is None:
                    bingo_claimed_by = 'player'
                    wallet += BINGO_PRIZE
                    print(f"You have BINGO! You win ${BINGO_PRIZE}. Wallet: ${wallet}")

                # After bingo, prompt for endless mode controls
                while True:
                    choice = input("Press 'e' to end this game, or 'r' to repeat again: ").strip().lower()
                    if choice == 'e':
                        session_active = False
                        round_active = False
                        break
                    if choice == 'r':
                        round_active = False
                        break
                    print("Invalid choice. Press 'e' or 'r'.")
                break
            if resp == "b":
                # Only allow player's bingo claim if nobody has already claimed bingo
                if bingo_claimed_by is not None:
                    print(f"Bingo already claimed by {bingo_claimed_by}. No prize for you.")
                    continue

                valid_bingo = validate_bingo_claim(player_ticket, player_marked_set)
                if valid_bingo:
                    bingo_claimed_by = 'player'
                    BINGO_PRIZE = LINE_PRIZE * 4
                    wallet += BINGO_PRIZE
                    print(f"Valid BINGO! You win ${BINGO_PRIZE}. Wallet: ${wallet}")
                    # Prompt for endless controls
                    while True:
                        choice = input("Press 'e' to end this game, or 'r' to repeat again: ").strip().lower()
                        if choice == 'e':
                            session_active = False
                            round_active = False
                            break
                        if choice == 'r':
                            round_active = False
                            break
                        print("Invalid choice. Press 'e' or 'r'.")
                    break
                else:
                    print("Invalid Bingo claim — not all numbers are drawn yet.")
                    continue
            # otherwise (Enter) just continue to next draw

        # round finished (either by bingo and choice, or by deck exhaustion)
        if not session_active:
            break

    print(f"Session finished. Final wallet: ${wallet}")


class NumberDrawer:
    """Simple drawer for numbers 1 to 90 with no duplicates.

    Usage:
        d = NumberDrawer(seed=42)
        n = d.draw_next()
        history = d.drawn()
        remaining = d.remaining_count()
    """

    def __init__(self, seed: Optional[int] = None):
        self._seed = seed
        self.reset(seed)

    def reset(self, seed: Optional[int] = None) -> None:
        if seed is None:
            seed = self._seed
        self._rnd = random.Random(seed)
        self._pool = list(range(1, 91))
        self._rnd.shuffle(self._pool)
        self._drawn: List[int] = []

    def draw_next(self) -> int:
        """Draw the next number. Raises StopIteration when pool exhausted."""
        if not self._pool:
            raise StopIteration("All numbers have been drawn")
        n = self._pool.pop(0)
        self._drawn.append(n)
        return n

    def drawn(self) -> List[int]:
        return list(self._drawn)

    def remaining(self) -> List[int]:
        return list(self._pool)

    def remaining_count(self) -> int:
        return len(self._pool)


if __name__ == "__main__":
    # run interactive demo that demonstrates buying a ticket, drawing and claiming a line
    play_interactive_demo()
