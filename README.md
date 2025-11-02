# mini-bingo
A lightweight **terminal-based 90-ball (UK) bingo** prototype.  
Built for clarity, teamwork, and test coverage — not production.  

# Overview

`mini-bingo` simulates a simple 90-ball bingo game following UK rules:

- 3 rows × 9 columns per ticket (15 numbers total)
- Each row has **5 numbers and 4 blanks**
- Numbers range **1–90**, drawn without replacement
- Player can **manually claim a line** (single row)
- Simple **wallet system** handles ticket costs and line prizes
- Fully playable in the terminal

This project is organized for modular development and collaborative ownership.
---

## Tests

This project includes a small test-suite that validates the 9x3 UK ticket
generation rules and a few behaviours. To run the tests locally you'll need
`pytest` installed — a `requirements.txt` is provided for convenience.

From the repository root (the directory that contains this `README.md`) run
these commands in PowerShell:

```powershell
# install test dependencies
py -3 -m pip install -r requirements.txt

# run the tests (quiet output)
py -3 -m pytest -q .\tests\test_ticket_generation.py
```

If you prefer to run the whole test-suite from the parent folder, refer to the
path `bingo-game\tests\...` instead. The test file inserts `src` into
`sys.path` so imports should work when running from the project root.

## Requirements

All test dependencies are listed in `requirements.txt`. Currently this file
includes `pytest` which is sufficient to run the project's tests.
# mini-bingo
A lightweight **terminal-based 90-ball (UK) bingo** prototype.  
Built for clarity, teamwork, and test coverage — not production.  

# Overview

`mini-bingo` simulates a simple 90-ball bingo game following UK rules:

- 3 rows × 9 columns per ticket (15 numbers total)
- Each row has **5 numbers and 4 blanks**
- Numbers range **1–90**, drawn without replacement
- Player can **manually claim a line** (single row)
- Simple **wallet system** handles ticket costs and line prizes
- Fully playable in the terminal

This project is organized for modular development and collaborative ownership.
---
