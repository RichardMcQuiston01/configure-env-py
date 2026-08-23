from configure_env.parser import parse_template
from configure_env.wizard import (
    detect_generation_hint,
    is_secret_field,
    is_section_header,
    run_wizard,
)

EXAMPLE = """\
# --- Application ---------------------------------------------
# development | production
APP_ENV=development

# --- Security ---------------------------------------------------
# Generate a strong key:  python -c "import secrets; print(secrets.token_hex(32))"
API_KEY=change_me_before_running

# Sent to an external service; must match its issued value.
CATALOG_API_KEY=
"""


def test_is_secret_field_matches_common_secret_names() -> None:
    assert is_secret_field("API_KEY")
    assert is_secret_field("CATALOG_API_KEY")
    assert is_secret_field("DB_PASSWORD")
    assert is_secret_field("AUTH_TOKEN")
    assert is_secret_field("client_secret")


def test_is_secret_field_false_for_normal_field() -> None:
    assert not is_secret_field("APP_PORT")
    assert not is_secret_field("CORS_ORIGINS")


def test_detect_generation_hint_parses_token_hex_argument() -> None:
    comments = ['# Generate a strong key:  python -c "...token_hex(32))"']

    assert detect_generation_hint(comments) == 32


def test_detect_generation_hint_returns_none_without_hint() -> None:
    comments = ["# Sent to an external service; must match its issued value."]

    assert detect_generation_hint(comments) is None


def test_is_section_header_matches_dashed_comment_line() -> None:
    assert is_section_header("# --- Application ---------------------------------")
    assert not is_section_header("# Generate a strong key: ...")


def test_run_wizard_keeps_default_on_blank_input() -> None:
    template = parse_template(EXAMPLE)
    prompts = iter(["", "n", "", ""])

    values = run_wizard(
        template,
        current_values={},
        prompt=lambda _: next(prompts),
        prompt_secret=lambda _: "",
        echo=lambda _: None,
    )

    assert values["APP_ENV"] == "development"


def test_run_wizard_uses_secret_prompt_and_keeps_current_on_blank() -> None:
    template = parse_template(EXAMPLE)

    values = run_wizard(
        template,
        current_values={"CATALOG_API_KEY": "existing-value"},
        prompt=lambda _: "n" if "generate" in _.lower() else "",
        prompt_secret=lambda _: "",
        echo=lambda _: None,
    )

    assert values["CATALOG_API_KEY"] == "existing-value"


def test_run_wizard_generates_secret_when_hinted_and_accepted() -> None:
    template = parse_template(EXAMPLE)

    values = run_wizard(
        template,
        current_values={},
        prompt=lambda _: "y" if "generate" in _.lower() else "",
        prompt_secret=lambda _: "should-not-be-used",
        echo=lambda _: None,
    )

    assert values["API_KEY"] != "should-not-be-used"
    assert len(values["API_KEY"]) == 64  # token_hex(32) -> 64 hex chars


def test_run_wizard_falls_back_to_manual_entry_when_generation_declined() -> None:
    template = parse_template(EXAMPLE)

    values = run_wizard(
        template,
        current_values={},
        prompt=lambda _: "n" if "generate" in _.lower() else "",
        prompt_secret=lambda _: "my-manual-key",
        echo=lambda _: None,
    )

    assert values["API_KEY"] == "my-manual-key"
