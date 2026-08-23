"""Parsing and rendering of .env / .env.example files.

Pure text in, text out: no I/O and no interaction here, so this module is
unit-testable without touching stdin or the filesystem.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_FIELD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
_INLINE_COMMENT_RE = re.compile(r"(?<=\s)#.*$")

OTHER_SECTION_HEADER = "# --- Other (not in .env.example) ---"


@dataclass(frozen=True)
class Field:
    key: str
    default_value: str
    inline_comment: str | None
    line_index: int


@dataclass(frozen=True)
class EnvTemplate:
    lines: tuple[str, ...]
    fields: tuple[Field, ...]


def _split_inline_comment(rest: str) -> tuple[str, str | None]:
    match = _INLINE_COMMENT_RE.search(rest)
    if match is None:
        return rest.rstrip(), None
    return rest[: match.start()].rstrip(), rest[match.start() :]


def parse_template(text: str) -> EnvTemplate:
    lines = text.splitlines()
    fields: list[Field] = []

    for index, line in enumerate(lines):
        match = _FIELD_RE.match(line)
        if match is None:
            continue
        key, rest = match.group(1), match.group(2)
        default_value, inline_comment = _split_inline_comment(rest)
        fields.append(
            Field(
                key=key,
                default_value=default_value,
                inline_comment=inline_comment,
                line_index=index,
            )
        )

    return EnvTemplate(lines=tuple(lines), fields=tuple(fields))


def render(
    template: EnvTemplate,
    values: dict[str, str],
    extra: dict[str, str] | None = None,
) -> str:
    lines = list(template.lines)

    for field in template.fields:
        value = values.get(field.key, field.default_value)
        comment_suffix = f"  {field.inline_comment}" if field.inline_comment else ""
        lines[field.line_index] = f"{field.key}={value}{comment_suffix}"

    output = "\n".join(lines)
    if not output.endswith("\n"):
        output += "\n"

    if extra:
        output += f"\n{OTHER_SECTION_HEADER}\n"
        for key, value in extra.items():
            output += f"{key}={value}\n"

    return output


def parse_simple_env(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        match = _FIELD_RE.match(line)
        if match is None:
            continue
        key, rest = match.group(1), match.group(2)
        value, _ = _split_inline_comment(rest)
        values[key] = value
    return values
