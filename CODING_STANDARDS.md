# CODING_STANDARDS (chimera-infra-new)

## Python
- Black formatting, 120 cols:
  - `black --line-length 120 app tests`
- Ruff linting rules (fast defaults):
  - `ruff check app tests`
- Type hints encouraged for public APIs.
- Pydantic models for request/response schemas.

## Testing
- Pytest for unit tests; aim for fast deterministic tests under 2s.
- Organize tests by module under `tests/`.
- Add regression tests when fixing bugs.

## Commits & PRs
- Conventional commits recommended (feat, fix, chore, docs, refactor, test, ci).
- Small, focused PRs (<300 LOC preferred) with description and checklist.
- CI must pass before merge.

## CI
- GitHub Actions runs `pip install -r requirements.txt` and `pytest -q`.
- Consider adding ruff and black check in future.

## Security & Config
- Optional bearer token via `CHIMERA_API_TOKEN` (never hardcode secrets).
- Validate inputs via pydantic; include minimal rate limiting in app layer.

## Docs
- Keep `README.md` updated with run, test, and deploy instructions.
- Document JSON protocol version and changes.
