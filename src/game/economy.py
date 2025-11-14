"""Economy helpers for the bingo game.

This module centralises the player's balance state and the reward logic so
future UI layers (CLI, GUI, tests) can all share the same persistence rules.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

DEFAULT_STARTING_BALANCE = 10
DEFAULT_TICKET_COST = 1
DEFAULT_LINE_PRIZE = 5
DEFAULT_BINGO_MULTIPLIER = 4


class BalanceManager:
    """Persist the player's wallet and expose reward helpers."""

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        starting_balance: int = DEFAULT_STARTING_BALANCE,
        ticket_cost: int = DEFAULT_TICKET_COST,
        line_prize: int = DEFAULT_LINE_PRIZE,
        bingo_prize: Optional[int] = None,
    ) -> None:
        root = Path(__file__).resolve().parents[2]
        if storage_path is None:
            storage_path = root / "data" / "wallet.json"
        self._storage_path = storage_path
        self._starting_balance = max(0, int(starting_balance))
        self.ticket_cost = max(0, int(ticket_cost))
        self.line_prize = max(0, int(line_prize))
        if bingo_prize is None:
            bingo_prize = self.line_prize * DEFAULT_BINGO_MULTIPLIER
        self.bingo_prize = max(0, int(bingo_prize))
        self._balance: Optional[int] = None

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def _ensure_loaded(self) -> None:
        if self._balance is not None:
            return
        self._balance = self._read_from_disk()

    def _read_from_disk(self) -> int:
        try:
            data = json.loads(self._storage_path.read_text())
            balance = int(data.get("balance", self._starting_balance))
        except FileNotFoundError:
            balance = self._starting_balance
        except (json.JSONDecodeError, ValueError, TypeError):
            # Treat malformed files as reset to starting balance.
            balance = self._starting_balance
        return max(0, balance)

    def _write_to_disk(self) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"balance": self._balance}
        self._storage_path.write_text(json.dumps(payload, indent=2))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_balance(self) -> int:
        self._ensure_loaded()
        assert self._balance is not None
        return self._balance

    def set_balance(self, value: int) -> int:
        self._balance = max(0, int(value))
        self._write_to_disk()
        return self._balance

    def adjust_balance(self, delta: int) -> int:
        self._ensure_loaded()
        assert self._balance is not None
        self._balance = max(0, self._balance + int(delta))
        self._write_to_disk()
        return self._balance

    def reset(self) -> int:
        self._balance = self._starting_balance
        self._write_to_disk()
        return self._balance

    # ------------------------------------------------------------------
    # Gameplay helpers
    # ------------------------------------------------------------------
    def can_afford_ticket(self, quantity: int = 1) -> bool:
        cost = self.ticket_cost * max(1, int(quantity))
        return self.get_balance() >= cost

    def spend_for_tickets(self, quantity: int = 1) -> int:
        quantity = max(1, int(quantity))
        cost = self.ticket_cost * quantity
        if not self.can_afford_ticket(quantity):
            raise ValueError("Insufficient balance to buy tickets")
        return self.adjust_balance(-cost)

    def award_line(self) -> int:
        return self.adjust_balance(self.line_prize)

    def award_bingo(self) -> int:
        return self.adjust_balance(self.bingo_prize)

    def deposit(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        return self.adjust_balance(amount)

    def withdraw(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive")
        if self.get_balance() < amount:
            raise ValueError("Insufficient funds")
        return self.adjust_balance(-amount)
