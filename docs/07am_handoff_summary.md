# 7 am handoff summary

Local timestamp: 2026-03-01 06:58 PST

## Current recommended default

- Primary day-of policy file:
  - `research_logs/experiment_outputs/dayof_policy_hybrid_v11_lcb.json`
- Default objective mapping in this policy:
  - `ev`: `meta_switch_soft`
  - `first_place`: `conservative`
  - `robustness`: `level_k`
- Why this default:
  - It preserves broad rule-profile/horizon coverage from global matrices.
  - It overlays human-opponent (hero-vs-pool) evidence where available.
  - Final focused high-sample rerun at `06:57 PST` confirmed `standard_rankings|first_place|h10|kingmaker -> conservative` by both mean and LCB.

## What is implemented and working

- Rule-profile aware game engine and evaluator:
  - `game/engine_base.py`
  - `game/rules.py`
  - `game/utils.py`
- Strategy system with parameterized specs:
  - `strategies/`
  - loader supports `tag|k=v|...`
- Simulation and experiment framework:
  - `sim/`
  - scripts under `scripts/`
- Live advisor API and HUD:
  - API: `game/api.py`
  - HUD: `web/src/routes/+page.svelte`
- Live correlation inference and auto condition routing:
  - `game/correlation.py`
  - API returns `correlation_inference`
  - advisor can auto-select condition key from inferred mode + `match_horizon`

## Startup commands

Backend:

```bash
SOLDEM_POLICY_PATH=research_logs/experiment_outputs/dayof_policy_hybrid_v11_lcb.json \
  uv run uvicorn game.api:app --host 127.0.0.1 --port 8000
```

HUD:

```bash
pnpm --dir web dev --host 127.0.0.1 --port 5173
```

Open:

- `http://127.0.0.1:5173`

## Day-of usage quick loop

1. Keep `auto policy condition` enabled in HUD unless testing manual overrides.
2. Set `match_horizon` to expected games (`3`, `7`, `10`, `20`, `30` supported by policy conditions).
3. Enter current state/cards/stacks, click recommendation.
4. Log bid/auction events so correlation inference updates.
5. For explicit table dynamics shifts, manually override `strategy_tag` if needed.

## Fast fallback options

- Conservative global fallback:
  - `research_logs/experiment_outputs/dayof_policy_global_v7_lcb.json`
- Baseline-only combined fallback:
  - `research_logs/experiment_outputs/dayof_policy_combined_baseline_v7_lcb.json`
- Hero-pool baseline-only policy:
  - `research_logs/experiment_outputs/hero_pool_policy_20260301_061711_lcb.json`

## Rule variation handling

- Use patch guide:
  - `docs/day_of_patch_guide.md`
- Apply rule profile quickly:

```bash
python scripts/apply_rule_patch.py --profile standard_rankings
```

or:

```bash
python scripts/apply_rule_patch.py --profile baseline_v1 --overrides '{"seller_can_bid_own_card": true}'
```

## Most important experiment outputs

- Long matrix family:
  - `research_logs/experiment_outputs/long_parallel_matrix_20260301_025448.*`
  - `research_logs/experiment_outputs/long_parallel_matrix_20260301_030443.*`
  - `research_logs/experiment_outputs/long_parallel_matrix_20260301_033913.*`
  - `research_logs/experiment_outputs/long_parallel_matrix_20260301_040636.*`
- Hero-pool family:
  - `research_logs/experiment_outputs/hero_pool_matrix_20260301_054854.*`
  - `research_logs/experiment_outputs/hero_pool_matrix_20260301_061711.*`
  - `research_logs/experiment_outputs/hero_pool_matrix_20260301_064413.*`
  - `research_logs/experiment_outputs/hero_pool_matrix_20260301_065716.*`

## Verification status

- Python unit tests pass (`11` tests).
- `pnpm --dir web check` passes.
- API bootstrap loads `dayof_policy_hybrid_v11_lcb.json` defaults correctly.

## If only one thing can be done right before play

- Start backend with `SOLDEM_POLICY_PATH=...dayof_policy_hybrid_v11_lcb.json`
- Keep HUD auto condition routing on.
- Keep event logging current so correlation inference is usable.
