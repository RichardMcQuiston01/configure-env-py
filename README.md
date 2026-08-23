# Configure Environment Files

## Overview

CLI Python scripts for configuring environment files for a various software and web applications available on the PyPi repository.

`configure-env` reads a project's `.env.example` template and walks you through
an interactive wizard to create or update the matching `.env` file:

- Shows each field's description and section headers, taken straight from the
  template's own comments.
- Prefills from an existing `.env`, if one is already there — press Enter to
  keep a value, or type a new one.
- Offers to auto-generate a value for any field whose comment documents a
  generation command (e.g. `secrets.token_hex(32)`), instead of making you
  copy-paste a separate command.
- Masks input for fields that look like secrets (name contains `KEY`,
  `SECRET`, `TOKEN`, or `PASSWORD`).
- Backs up an existing `.env` to `.env.bak` before overwriting it, and
  preserves any keys already in `.env` that aren't in `.env.example` instead
  of silently dropping them.

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

From PyPI (once published):

```bash
pip install configure-env-py
```

From GitHub, before the first PyPI release:

```bash
pip install git+https://github.com/RichardMcQuiston01/configure-env-py.git
```

### Usage

```bash
configure-env [directory]
```

`directory` defaults to the current directory. `configure-env` looks for
`<directory>/.env.example` there and writes/updates `<directory>/.env`.

### Examples

Run from a project root that already contains `.env.example`:

```bash
$ configure-env
Application
-----------
APP_ENV [development]:
...
Security
--------
  Generate a strong key:  python -c "import secrets; print(secrets.token_hex(32))"
API_KEY - generate a secure random value automatically? [Y/n]:
  generated API_KEY (shown once, also saved to .env): 3f1c9c...
...
wrote .env
```

Target a different directory:

```bash
configure-env ../some-other-project
```

## Development

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"

pytest
ruff check .
mypy src
```

## License

Apache 2.0 — see [LICENSE](./LICENSE).

## Support

If this library saved you some reverse-engineering, consider buying me a coffee. ☕

[**Donate via Stripe**](https://donate.stripe.com/00w5kD3Gj1Xo9v7gVOcs800), or scan:

[![Donate via Stripe](./donate.svg)](https://donate.stripe.com/00w5kD3Gj1Xo9v7gVOcs800)

## Copyright

(c) 2026 Richard McQuiston. Licensed under the Apache License, Version 2.0 — see [COPYRIGHT](./COPYRIGHT).
