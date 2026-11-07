# CHANGELOG

## [Unreleased]

### Changed

- Donations now point at Ko-fi instead of Stripe: the README badge, a `Funding` project URL and a new `.github/FUNDING.yml`. The Stripe QR image is removed.

## [0.1.0] - 2026-08-23

### Added

- Initial release of `configure-env`, an interactive CLI wizard that creates
  or updates a `.env` file from a `.env.example` template.
- Detects fields whose `.env.example` comment documents a generation command
  (e.g. `secrets.token_hex(32)`) and offers to auto-generate a secure value.
- Masks input for fields that look like secrets (name contains `KEY`,
  `SECRET`, `TOKEN`, or `PASSWORD`); falls back to visible input with a
  warning when stdin isn't a real terminal, instead of hanging (Windows'
  `getpass` reads from the console directly and ignores redirected stdin).
- Prefills from an existing `.env`, backs it up to `.env.bak` before
  overwriting, and preserves any keys present in the old `.env` but absent
  from `.env.example` under an appended "Other" section rather than
  dropping them.
