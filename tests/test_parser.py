from configure_env.parser import parse_simple_env, parse_template, render

EXAMPLE = """\
# ------------------------------------------------------------
# example configuration
# ------------------------------------------------------------

# --- Application ---------------------------------------------
APP_ENV=development          # development | production
APP_PORT=8000

# --- Security ---------------------------------------------------
# Generate a strong key:  python -c "import secrets; print(secrets.token_hex(32))"
API_KEY=change_me_before_running

# Optional: leave blank to disable.
CATALOG_API_URL=
"""


def test_parse_template_extracts_fields_in_file_order() -> None:
    template = parse_template(EXAMPLE)

    keys = [field.key for field in template.fields]
    assert keys == ["APP_ENV", "APP_PORT", "API_KEY", "CATALOG_API_URL"]


def test_parse_template_captures_defaults_and_inline_comments() -> None:
    template = parse_template(EXAMPLE)
    by_key = {field.key: field for field in template.fields}

    assert by_key["APP_ENV"].default_value == "development"
    assert by_key["APP_ENV"].inline_comment == "# development | production"
    assert by_key["APP_PORT"].default_value == "8000"
    assert by_key["APP_PORT"].inline_comment is None
    assert by_key["CATALOG_API_URL"].default_value == ""


def test_render_without_changes_reproduces_defaults() -> None:
    template = parse_template(EXAMPLE)
    defaults = {field.key: field.default_value for field in template.fields}

    output = render(template, defaults)

    assert "APP_ENV=development  # development | production" in output
    assert "APP_PORT=8000" in output
    assert "CATALOG_API_URL=" in output


def test_render_substitutes_new_values_and_keeps_inline_comment() -> None:
    template = parse_template(EXAMPLE)
    values = {
        "APP_ENV": "production",
        "APP_PORT": "9000",
        "API_KEY": "abc123",
        "CATALOG_API_URL": "https://example.test",
    }

    output = render(template, values)

    assert "APP_ENV=production  # development | production" in output
    assert "APP_PORT=9000" in output
    assert "API_KEY=abc123" in output
    assert "CATALOG_API_URL=https://example.test" in output


def test_render_appends_extra_keys_under_other_section() -> None:
    template = parse_template(EXAMPLE)
    defaults = {field.key: field.default_value for field in template.fields}

    output = render(template, defaults, extra={"LEGACY_FLAG": "true"})

    assert "# --- Other (not in .env.example) ---" in output
    assert "LEGACY_FLAG=true" in output


def test_render_omits_other_section_when_no_extra_keys() -> None:
    template = parse_template(EXAMPLE)
    defaults = {field.key: field.default_value for field in template.fields}

    output = render(template, defaults, extra={})

    assert "Other (not in .env.example)" not in output


def test_parse_simple_env_ignores_comments_and_blank_lines() -> None:
    text = "\n".join(
        [
            "# a comment",
            "",
            "APP_ENV=production",
            "API_KEY=abc123  # trailing comment",
        ]
    )

    values = parse_simple_env(text)

    assert values == {"APP_ENV": "production", "API_KEY": "abc123"}
