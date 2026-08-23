"""Interactive prompting for configure-env.

The prompt/prompt_secret/echo callables are injected so this module is
testable with fakes instead of real stdin.
"""

from __future__ import annotations

import getpass
import re
import secrets
from collections.abc import Callable

from configure_env.parser import EnvTemplate, Field

_SECRET_NAME_RE = re.compile(r"(KEY|SECRET|TOKEN|PASSWORD)", re.IGNORECASE)
_GENERATION_HINT_RE = re.compile(r"token_hex\((\d+)\)")
_HEADER_RE = re.compile(r"^#\s*-{3,}.*-{3,}\s*$")

Prompt = Callable[[str], str]
Echo = Callable[[str], None]


def is_secret_field(key: str) -> bool:
    return bool(_SECRET_NAME_RE.search(key))


def detect_generation_hint(comment_lines: list[str]) -> int | None:
    for line in comment_lines:
        match = _GENERATION_HINT_RE.search(line)
        if match is not None:
            return int(match.group(1))
    return None


def is_section_header(line: str) -> bool:
    return bool(_HEADER_RE.match(line))


def generate_secret(num_bytes: int) -> str:
    return secrets.token_hex(num_bytes)


def _describe_preamble(preamble: list[str], echo: Echo) -> list[str]:
    comment_lines: list[str] = []
    for line in preamble:
        stripped = line.strip()
        if not stripped:
            continue
        if is_section_header(line):
            title = stripped.strip("#").strip(" -")
            echo("")
            echo(title)
            echo("-" * len(title))
        elif stripped.startswith("#"):
            comment_lines.append(stripped)
            echo(f"  {stripped.lstrip('#').strip()}")
    return comment_lines


def _prompt_for_field(
    field: Field,
    current: str,
    comment_lines: list[str],
    *,
    prompt: Prompt,
    prompt_secret: Prompt,
    echo: Echo,
) -> str:
    generate_bytes = detect_generation_hint(comment_lines)
    secret = is_secret_field(field.key)

    if generate_bytes is not None:
        answer = prompt(
            f"{field.key} - generate a secure random value automatically? [Y/n]: "
        ).strip().lower()
        if answer in ("", "y", "yes"):
            value = generate_secret(generate_bytes)
            echo(f"  generated {field.key} (shown once, also saved to .env): {value}")
            return value

    if secret:
        echo(f"  current: {'(hidden)' if current else '(not set)'}")
        entered = prompt_secret(
            f"{field.key} - new value (leave blank to keep current): "
        )
        value = entered if entered else current
    else:
        entered = prompt(f"{field.key} [{current}]: ").strip()
        value = entered if entered else current

    if "#" in value:
        echo(
            f"  warning: value for {field.key} contains '#', which some .env "
            "readers may parse as the start of a comment"
        )

    return value


def run_wizard(
    template: EnvTemplate,
    current_values: dict[str, str],
    *,
    prompt: Prompt = input,
    prompt_secret: Prompt = getpass.getpass,
    echo: Echo = print,
) -> dict[str, str]:
    collected: dict[str, str] = {}
    prev_index = -1

    for field in template.fields:
        preamble = list(template.lines[prev_index + 1 : field.line_index])
        prev_index = field.line_index

        comment_lines = _describe_preamble(preamble, echo)
        current = current_values.get(field.key, field.default_value)
        collected[field.key] = _prompt_for_field(
            field,
            current,
            comment_lines,
            prompt=prompt,
            prompt_secret=prompt_secret,
            echo=echo,
        )

    return collected
