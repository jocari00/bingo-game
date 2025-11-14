"""Project entrypoint: run this file to start the bingo CLI.

This is the single top-level entrypoint users should run per the README.
It ensures the `src` package folder is on `sys.path` and then invokes the
interactive game loop. Use `--reset-wallet` to reset the persisted wallet.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys


def _ensure_src_on_path():
    root = Path(__file__).resolve().parent
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main(argv=None):
    parser = argparse.ArgumentParser(description="mini-bingo CLI runner")
    parser.add_argument("--reset-wallet", action="store_true", help="Reset persisted wallet to starting balance")
    args = parser.parse_args(argv)

    _ensure_src_on_path()

    # Import package modules after src is on sys.path. Use a resilient import
    # approach so running the file directly works for new users.
    try:
        from game.economy import BalanceManager
        from game.main import play_interactive_demo
    except Exception:
        # If package import doesn't work, load modules by file path
        import importlib.util

        root = Path(__file__).resolve().parent
        src = root / "src"
        game_dir = src / "game"

        def _load_module_from(path: Path, module_name: str):
            spec = importlib.util.spec_from_file_location(module_name, str(path))
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load module {module_name} from {path}")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod

        econ_mod = _load_module_from(game_dir / "economy.py", "game.economy")
        main_mod = _load_module_from(game_dir / "main.py", "game.main")

        BalanceManager = econ_mod.BalanceManager
        play_interactive_demo = main_mod.play_interactive_demo

    bm = BalanceManager()
    if args.reset_wallet:
        bm.reset()
        print(f"Wallet reset to ${bm.get_balance()}")

    play_interactive_demo()


if __name__ == "__main__":
    main()
