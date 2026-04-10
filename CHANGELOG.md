# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-04-10

### Added
- Integrated cache usage in weather, forecast, and geocode tool paths.
- Added API key format validation for Anthropic, OpenAI, and OpenWeatherMap.
- Added stronger input sanitization and a simple rate limiter utility.
- Added user-friendly exception messaging for CLI and agent flows.
- Added CI workflow (`.github/workflows/ci.yml`) for lint, type checks, and tests.
- Added project `README.md` with install, config, usage, and release checks.

### Changed
- Updated Pydantic model config to `ConfigDict` for modern compatibility.
- Improved tool execution robustness in agent flow (input validation and safer parsing).
- Improved type safety across source modules and fixed strict mypy issues.
- Repaired packaging script in `setup.py`.

### Fixed
- Fixed lint issues across source and tests.
- Fixed strict typing failures in provider SDK integration paths.
- Fixed release-blocking setup script syntax errors.

### Verification
- `ruff check src tests` passed.
- `mypy src --ignore-missing-imports` passed.
- `pytest tests -q` passed (38 passed).
- CLI smoke checks passed (`--help`, `version`).