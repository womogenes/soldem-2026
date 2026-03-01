# Pre-7 final checklist

Local time: 2026-03-01 05:50 PST

## Purpose

Provide a fixed, low-latency runbook for the final 20 minutes before the 7:00 am PT game start.

## T-20 to T-15 minutes

1. Start backend and HUD.
- `uv run uvicorn game.api:app --host 0.0.0.0 --port 8000`
- `pnpm -C web dev --host`

2. Run full preflight if time permits.
- `bash scripts/day_of_preflight.sh --api-url http://127.0.0.1:8000 --pb-url http://18.204.1.6:8090 --with-tests --with-web`

3. Always run policy smoke if only one check can be done.
- `bash scripts/day_of_preflight.sh --api-url http://127.0.0.1:8000 --with-policy-smoke`

## T-15 to T-10 minutes

1. Apply announced rules.
- `uv run python scripts/day_of_patch.py --preset baseline --overrides-json '<host json>'`

2. Refresh HUD session panel.
- Verify `resolved_champions` and `First-place routing cues`.
- Verify `resolved_champion_reasons.first_place` is sensible.

3. If rules are unusual and time remains, run autosolve once.
- `uv run python scripts/day_of_autosolve_patch.py --rule-profile baseline_v1 --overrides-json '<host json>' --n-tables 12 --n-games 8 --seed 42`

## T-10 to T-5 minutes

1. Run three fast mock auctions in HUD with event logging.
2. Confirm recommendation latency is acceptable.
3. Keep objective at `ev` by default unless tournament context requires upside.

## T-5 to T-0 minutes

1. Freeze to stable settings.
- Do not run large recomputations.
- Keep known-good API/HUD tabs open.

2. Confirm fallback command set is ready.
- Re-apply rules quickly:
  - `uv run python scripts/day_of_patch.py --preset baseline --overrides-json '<host json>'`
- Re-run policy smoke quickly:
  - `bash scripts/day_of_preflight.sh --api-url http://127.0.0.1:8000 --with-policy-smoke`

## During games

1. Start on `ev` and use `Use objective champion`.
2. Log events continuously (`bid`, `auction_result`).
3. Use `first_place` only when upside is needed and trigger context supports it.
4. Trust deterministic recommendation first; use LLM hint as secondary context.

## Current first-place trigger reference

- exact baseline: `meta_switch`
- sprint + winner-takes-all: `pot_fraction`
- high-ante + winner-takes-all (`n_orbits>=3` and (`ante/start>=0.26` or `ante>=50`)): `pot_fraction`
- passive high-confidence table read: `pot_fraction`
- otherwise: `equity_evolved_v1`
