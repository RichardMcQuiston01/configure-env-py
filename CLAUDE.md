# CLAUDE.md — configure-env-py

This file is read by Claude Code to understand the project layout,
conventions, and commands. Keep it up to date as the project evolves.

## Overview

`configure-env-py` is a CLI Python package, published to PyPI as
`configure-env-py` (installed console command: `configure-env`), that turns a
project's `.env.example` template into an interactive wizard for creating or
updating the matching `.env` file.

## Repository layout

```
configure-env-py/
├── src/configure_env/
│   ├── __init__.py     ← package version
│   ├── __main__.py     ← `python -m configure_env` entry point
│   ├── cli.py           ← argparse wiring, stdout/stdin handling, main()
│   ├── parser.py        ← pure .env.example / .env parsing + rendering
│   └── wizard.py        ← interactive prompt logic, secret/generation heuristics
├── tests/
│   ├── test_parser.py
│   └── test_wizard.py
├── pyproject.toml
├── LICENSE               ← Apache-2.0
├── COPYRIGHT
├── README.md
└── CHANGELOG.md
```

## Commands

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"

# Test
pytest

# Lint / type-check
ruff check .
mypy src

# Run locally without installing
python -m configure_env [directory]

# Build + publish (manual, until CI is set up)
python -m build
twine upload dist/*              # add --repository testpypi to test first
```

## Design notes

- **Zero runtime dependencies** — stdlib only (`argparse`, `getpass`,
  `secrets`). Deliberate: this tool handles secret values, so fewer
  supply-chain dependencies is a feature, not an oversight.
- `parser.py` is pure (parse text in, render text out) and unit-tested
  directly. `wizard.py`'s interactive loop takes injectable
  `prompt`/`prompt_secret`/`echo` callables so it's testable with fakes
  instead of real stdin.
- A field is treated as secret (masked input) if its name contains `KEY`,
  `SECRET`, `TOKEN`, or `PASSWORD` (case-insensitive).
- A field only offers auto-generation if its `.env.example` comment
  documents a `secrets.token_hex(N)` call. This is deliberately narrower
  than "any secret-looking field" — a field like an externally-issued API
  key must match another system's value, and blindly generating one for it
  would produce a plausible-looking but wrong value.
- `cli.py` reconfigures stdout/stderr to UTF-8 with `errors="replace"`
  before printing anything, because `.env.example` banner comments can
  contain non-ASCII characters (e.g. box-drawing separators) that crash on
  legacy Windows console codepages otherwise.
- On Windows, `getpass.getpass()` reads from the console handle directly and
  ignores redirected stdin — it hangs forever instead of raising when stdin
  is piped (CI, automation, non-interactive testing). `cli.py` checks
  `sys.stdin.isatty()` and falls back to plain (echoed) `input()` with a
  printed warning in that case, mirroring `getpass`'s own Unix fallback
  behavior rather than hanging.

## Versioning

Semantic versioning. Bump `version` in `pyproject.toml` and
`src/configure_env/__init__.py` together, and add a CHANGELOG entry, for
every release.
