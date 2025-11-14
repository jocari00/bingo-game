# mini-bingo
A lightweight **terminal-based 90-ball (UK) bingo** prototype.  
Built for clarity, teamwork, and test coverage — not production.  
# mini-bingo

A lightweight terminal-based 90-ball (UK) bingo prototype. Built for
clarity, teamwork, and test coverage — not production.

Overview

- 3 rows × 9 columns per ticket (15 numbers total)
- Each row has 5 numbers and 4 blanks
- Numbers range 1–90, drawn without replacement
- Player can manually claim a line (single row)
- Wallet system persists balance between runs
- Fully playable from the terminal via a single `main.py` entrypoint

Quick start (run the main entrypoint)

From the project root run:

```powershell
cd C:\Users\franc\bingo-project\bingo-game
py -3 main.py            # launch the interactive demo
py -3 main.py --reset-wallet   # reset persisted wallet then launch
```

Alternatively you can run the package directly from `src`:

```powershell
cd src
py -3 -m game.game
```

Tests

Install test deps and run pytest from the project root:

```powershell
py -3 -m pip install -r requirements.txt
py -3 -m pytest -q
```

Balance & Rewards

- Wallet is persisted in `data/wallet.json` inside the project folder.
- Defaults: ticket cost = $1, line prize = $5, bingo prize = 4× line prize.
- Use `--reset-wallet` to reset the wallet to the starting balance.

Notes for contributors

- The canonical entrypoint is `main.py` at the project root. Other modules
	in `src/game` are libraries and will not be executed unless called from
	`main.py` or the package. This keeps the project behavior predictable for
	new users.

If you want a different project structure or a console script entrypoint,
I can add a small setup or script to make installation easier.
This project is organized for modular development and collaborative ownership.
