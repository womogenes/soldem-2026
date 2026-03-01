# 7am handoff summary

Local timestamp: 2026-03-01 03:10:00 PST

## What is ready

- Strategy plugin framework (built-ins and external Python strategy files).
- Long-run validation artifacts with multi-seed, multi-horizon, multi-correlation evidence.
- API/HUD integrated with profile-aware champion defaults.
- PocketBase deployment and sync tooling operational.
- Day-of runbook and under-2-minute patch workflow documented.

## Final champion policy

- `ev`: `market_maker_tight`
- `first_place`: `market_maker_tight`
- `robustness`: `regime_switch_robust`

High-variance override:

- `first_place` pure win-rate mode can use `pot_fraction`, but this generally sacrifices expected PnL.

## Evidence highlights

From long validation matrix (`450` matches/cell seed, `3` seeds, horizons `5,10,20`, correlations `none,respect,herd,kingmaker`):

- `market_maker_tight` won all EV cells (`12/12`).
- `market_maker_tight` won all first-place cells (`12/12`).
- `regime_switch_robust` won all robustness cells (`12/12`).

From rule-profile validation (`320` matches/cell seed, `3` seeds, `6` rule profiles):

- `market_maker_tight` won all EV profile cells (`6/6`) and first-place profile cells (`6/6`).
- `regime_switch_robust` won all robustness profile cells (`6/6`).

From extreme correlation stress testing (`81` scenarios):

- EV winners were led by `market_maker_tight` (`50/81`) with `regime_switch_robust` second (`23/81`).
- First-place metric winners frequently became high-variance styles (`pot_fraction`/`random`), so they are treated as optional desperation overrides only.

## Fast start commands

### 1) Start advisor backend

```bash
uv run uvicorn game.api:app --host 127.0.0.1 --port 8000
```

### 2) Start HUD

```bash
pnpm --dir web dev --host 127.0.0.1 --port 5173
```

### 3) Open HUD

- `http://127.0.0.1:5173`

### 4) Verify API

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/session/state
```

## Day-of patch in under 2 minutes

```bash
uv run python scripts/apply_rule_patch.py --profile baseline_v1 --overrides '{"seller_can_bid_own_card": true}'
```

Full recipes: `docs/day_of_patch_guide.md`.

## PocketBase status

- Active instance: `i-08f41ea7a4d11aaca`
- URL: `http://44.221.42.217:8090`
- Bootstrap: `scripts/pocketbase_bootstrap.py`
- Sync: `scripts/sync_experiments_to_pocketbase.py`

## Rule-profile fallback map

See `research_logs/champion_lookup_from_rule_profile_validation_long.json`.

## Required reference for future rollouts

During compaction/handoff, include `research_logs/000_god_prompt.md` in required context.
