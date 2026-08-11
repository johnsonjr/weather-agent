# Weather Agent — Hardening Plan (Recommendation Review)

## Context
Repo review found 4 critical bugs, 6 structural weaknesses, and test/tooling gaps. `README.md:23-109` architecture is accurate. This plan sequences fixes by risk/effort so P0 bugs land first, P1 correctness second, P2 hygiene last.

## Goals
- Fix all P0 runtime bugs without behavior regressions.
- Close cache/config/packaging correctness gaps.
- Add minimal tooling (`pyproject.toml`, `ruff`/`mypy` config) and expand test coverage to >70%.

## Non-Goals
- No new features (voice, alerts, Redis, historical data).
- No LLM provider swap or async rewrite (track as future enhancement per `agent.md:228`).

## Triaged Findings

### P0 — Blocks Correctness (fix first)
| # | File | Issue | Impact | Fix |
|---|------|-------|--------|-----|
| 1 | `src/agent.py:280-340` | Tool execution loop duplicated — each tool runs twice; second iteration drops `used_tools`/`formatted_result` tracking | Double API cost, wrong `tool_used`, duplicate history | Collapse to single loop; keep error-append `result: f"Error:..."` path |
| 2 | `src/agent.py:438-442` | Invalid dict-comp `{"content": [...] for block in ...}` — SyntaxError / only-last-block-kept | Anthropic second-turn response broken | Replace with `{"content": [{"type":"text","text": b.text} for b in response.content if hasattr(b,"text")]}` |
| 3 | `src/agent.py:346` | `str(response.get("content",[]))` destroys structure in `conversation_history` | Degrades follow-up turns, wastes tokens | Store structured `response["content"]` or `message` consistently |
| 4 | `src/tools.py:52` | `if retries is None` unreachable (default `3`) | Dead code, confusing retry contract | Change signature to `retries: Optional[int]=None` and fallback to `self.max_retries`; remove obsolete `if retries is None` else branch |

### P1 — Correctness / Packaging
| # | File | Issue | Fix |
|---|------|-------|-----|
| 5 | `src/cache.py:206` | `invalidate()` clears `weather_cache`/`geocode_cache` only, not `forecast_cache` | Also delete `forecast_cache` keys for `city:{units}:{days}` variants or clear all matching prefix |
| 6 | `src/cli.py:94` | `forecast --days` no range validation (tool clamps 1-5 silently) | Add `click.IntRange(1,5)` or explicit check with `user_message` error |
| 7 | `setup.py:32` | `find_packages()` misses `src` layout (no `package_dir`) | Add `package_dir={"": "src"}` or migrate packaging to `pyproject.toml`; verify `pip install -e .` and `weather-agent` entry point |
| 8 | `requirements.txt:7` | `httpx>=0.25.0` unused (all calls use `requests`) | Remove, or implement `AsyncWeatherTool` sketched in `agent.md:228` — decision needed |
| 9 | `src/config.py:15-16` | Class-level `_config={}` mutable shared across instances; singleton fragile + `_config["logging"]["level"]="DEBUG"` mutates global in `cli.py:28` | Move `_config` to instance attr, init via `__new__` guard; or keep singleton but use instance dict; add `reset_for_tests()` helper |

### P2 — Quality / Tooling
| # | File | Issue | Fix |
|---|------|-------|-----|
| 10 | (new) `pyproject.toml` | No `pyproject.toml`/`ruff`/`mypy` config — CI installs `types-*` ad-hoc | Add `pyproject.toml` with `[project]`, `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest]`; keep `setup.py` shim or remove |
| 11 | `tests/` | ~38% coverage (only `test_weather.py`); no agent/cli/config/cache edge tests | Add `test_agent.py`, `test_cli.py`, `test_cache.py`, `test_config.py`; mock LLM + `responses` for API errors (401/404/429/5xx/timeout) |
| 12 | Misc | `src/utils.py:SimpleRateLimiter` not wired; `logging_utils.py:32` duplicate handlers guard is correct but `get_logger` bypasses it; `main.py` thin wrapper — consider consolidating | Wire or document `SimpleRateLimiter`; ensure `setup_logging` idempotent; keep `main.py` for `python main.py` compat |

## Execution Phases

### Phase 1 — P0 Hotfixes (est. 45 min)
1. Branch `fix/p0-agent-tool-loop` (or single `fix/hardening`).
2. Patch `src/agent.py:275-382` — dedupe loop; fix 438-442 comprehension; fix history store; add regression test for single-execution + anthropic builder.
3. Patch `src/tools.py:51-53` — fix retries signature.
4. Verify: `pytest tests -q` + manual `anthropic` mock.

### Phase 2 — P1 Correctness (est. 40 min)
5. Patch `src/cache.py:206` invalidate.
6. Patch `src/cli.py:92-93` days validation.
7. Patch `setup.py:24-32` packaging (+ smoke `pip install -e .`).
8. Decide `httpx` — remove from `requirements.txt` or gate behind `extras`.
9. Refactor `src/config.py` singleton; add `Config.clear_instance()` for tests; ensure `cli --debug` doesn't leak mutated config.

### Phase 3 — P2 Tooling & Coverage (est. 60 min)
10. Add `pyproject.toml` (ruff target `py310`, line 100; mypy `ignore_missing_imports=false` with explicit overrides).
11. Expand tests to cover exceptions, utils sanitization, cache hit/miss, agent `chat()` empty/LLM error paths, CLI `weather` validation (`cli.py:42-50`).
12. Run hygiene: `ruff check src tests --fix` + `ruff format`; `mypy src --ignore-missing-imports` zero new errors; `pytest --cov=src --cov-fail-under=70`.

## Risks & Mitigations
- **Singleton refactor breaks global `get_config()`**: Mitigate by preserving `get_config()` API, add tests for `Config()` reuse.
- **Packaging change breaks entry point**: Smoke test `weather-agent --help` and `python -m src.cli --help` after change.
- **LLM mock brittleness**: Isolate Anthropic/OpenAI mocks behind helper; don't require live keys in CI (use `responses` + `unittest.mock`).
- **Cache TTL flakiness in tests**: Use freezegun or inject TTL=1 for deterministic expiry tests.

## Validation Checklist (matches `README.md:475`)
- [ ] `ruff check src tests` clean
- [ ] `mypy src --ignore-missing-imports` — no new errors (pre-existing `models.py:36` `ConfigDict` warning stays)
- [ ] `pytest tests -q` green; `--cov` >=70% if enforced
- [ ] `pip install -e .` + `weather-agent --help` + `python main.py` smoke
- [ ] Forecast `days=0`/`6`/`"abc"` rejected with user-friendly message
- [ ] Agent single tool call executes exactly once (spy on `WeatherTool.get_weather`)

## Open Questions for Owner
1. Keep or drop `httpx`? (Recommend drop until async milestone.)
2. Target coverage gate — 70% or 80%?
3. Keep `setup.py` shim or fully migrate to `pyproject.toml`?

## Next Step
Approve plan → execute Phase 1 immediately; Phases 2/3 can be parallelized after P0 lands.
