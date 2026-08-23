from __future__ import annotations

import argparse
import getpass
import shutil
import sys
from pathlib import Path

from configure_env import __version__
from configure_env.parser import parse_simple_env, parse_template, render
from configure_env.wizard import Prompt, run_wizard


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="configure-env",
        description=(
            "Interactively create or update a .env file from a .env.example "
            "template."
        ),
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="directory containing .env.example (default: current directory)",
    )
    parser.add_argument(
        "--version", action="version", version=f"configure-env {__version__}"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    # .env.example files may contain non-ASCII banner characters (e.g. box
    # drawing). Legacy Windows console codepages can't encode those; replace
    # rather than crash the wizard mid-way through.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")

    args = _build_parser().parse_args(argv)

    target_dir = Path(args.directory)
    example_path = target_dir / ".env.example"
    env_path = target_dir / ".env"

    if not example_path.is_file():
        print(f"error: no .env.example found in {target_dir}", file=sys.stderr)
        return 1

    template = parse_template(example_path.read_text(encoding="utf-8"))

    current_values: dict[str, str] = {}
    if env_path.is_file():
        current_values = parse_simple_env(env_path.read_text(encoding="utf-8"))

    # getpass reads from the console directly on Windows, ignoring redirected
    # stdin, and blocks forever if there is none. Fall back to plain (echoed)
    # input in that case rather than hang, matching getpass's own Unix
    # fallback behavior when it can't disable echo.
    prompt_secret: Prompt = getpass.getpass
    if not sys.stdin.isatty():
        print(
            "warning: stdin is not a terminal; secret values will be echoed, "
            "not hidden",
            file=sys.stderr,
        )
        prompt_secret = input

    collected = run_wizard(template, current_values, prompt_secret=prompt_secret)

    template_keys = {field.key for field in template.fields}
    extra_keys = {
        key: value for key, value in current_values.items() if key not in template_keys
    }
    if extra_keys:
        names = ", ".join(sorted(extra_keys))
        print(
            f"warning: keeping {len(extra_keys)} key(s) from the existing .env "
            f"not found in .env.example: {names}"
        )

    output = render(template, collected, extra_keys)

    if env_path.is_file():
        backup_path = target_dir / ".env.bak"
        shutil.copyfile(env_path, backup_path)
        print(f"backed up existing .env to {backup_path}")

    env_path.write_text(output, encoding="utf-8")
    print(f"wrote {env_path}")
    return 0
