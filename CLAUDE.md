# CLAUDE.md — configure-env-py

This file is read by Claude Code to understand the project layout,
conventions, and commands. Keep it up to date as the project evolves.

## Overview

`configure-env-py` is a CLI Python package, published to PyPI as
`configure-env` (installed console command: `configure-env`), that turns a
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

# Build locally (sanity check before tagging a release)
python -m build
twine check dist/*
```

## Publishing

Publishing is automated via GitHub Actions Trusted Publishing (OIDC — no
stored API token) in `.github/workflows/workflow.yml`. The workflow filename
must stay exactly `workflow.yml` — it's the value registered in the pending
publisher config on both pypi.org and test.pypi.org, and Trusted Publishing
matches on owner/repo/workflow filename (and environment, left blank on both).

Three-branch model:

- `dev` — working branch, unpublished. Push here freely; nothing in the
  workflow triggers off it.
- `staging` — push here to publish to **TestPyPI** as project `configure-env`,
  for validating packaging/install before promoting to `main`.
- `main` — push here to publish to **real PyPI** as project `configure-env`.

All jobs run `test → build`, then branch by which branch was pushed to. There
is no version gate on either publish path — every push to `staging` or
`main` must have a bumped version (see below) or the publish step fails
outright (PyPI/TestPyPI reject re-uploading an existing version; they do not
silently overwrite).

Typical flow: merge `dev` → `staging` (bump version if not already bumped),
confirm the TestPyPI publish and install work, then merge `staging` → `main`
to publish for real.

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
