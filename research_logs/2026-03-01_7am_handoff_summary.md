# 7am handoff summary

Local timestamp: 2026-03-01 01:48:00 PST

## What is ready

- Strategy search framework with pluggable strategy tags and external strategy-file support.
- New strategy family integrated and tested: `market_maker`, `conservative_ultra`, `elastic_conservative`, `conservative_plus`, `mc_edge`.
- HUD advisor API defaults set to empirically strongest choices:
  - `ev`: `market_maker`
  - `first_place`: `market_maker`
  - `robustness`: `conservative_ultra`
- Experiment artifacts produced:
  - `research_logs/experiment_outputs/candidates_*.json`
  - `research_logs/experiment_outputs/horizon_correlation_matrix.json`
  - `research_logs/experiment_outputs/rule_variant_matrix.json`
- PocketBase deployed and populated with strategy/evaluation records.
- Day-of runbooks and patch guides prepared under `docs/`.

## Empirical conclusion

- `market_maker` is the best default in almost all tested conditions.
- `conservative_ultra` is the primary robustness fallback under adverse correlation/high-variance conditions.
- Under `standard_rankings` + first-place objective, `conservative` can outperform.

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

Use:

```bash
uv run python scripts/apply_rule_patch.py --profile baseline_v1 --overrides '{"seller_can_bid_own_card": true}'
```

Full recipes are in `docs/day_of_patch_guide.md`.

## PocketBase status

- Active instance: `i-08f41ea7a4d11aaca`
- URL: `http://44.221.42.217:8090`
- Bootstrap collections script: `scripts/pocketbase_bootstrap.py`
- Sync script: `scripts/sync_experiments_to_pocketbase.py`

## Strategy by rule-profile fallback

- `baseline_v1`: `market_maker` (`ev`, `first_place`), `conservative_ultra` (`robustness`)
- `standard_rankings`: `market_maker` (`ev`), `conservative` (`first_place`), `conservative_ultra` (`robustness`)
- `seller_self_bid`: `market_maker` (all)
- `top2_split`: `market_maker` (all)
- `high_low_split`: `market_maker` (all)
- `single_card_sell`: `market_maker` (`ev`, `first_place`), `conservative_ultra` (`robustness`)

## Required reference for future rollouts

During compaction/handoff, include `research_logs/000_god_prompt.md` in the required context.
